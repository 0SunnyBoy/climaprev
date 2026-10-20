import binascii
import hashlib
import io
import json
import re
import struct
import zipfile
import zlib
from pathlib import Path

import httpx

URL = 'https://portal.inmet.gov.br/uploads/dadoshistoricos/2025.zip'
AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36'
root = Path('.historical-reports/inmet')
root.mkdir(parents=True, exist_ok=True)
requests = []
with httpx.Client(headers={'User-Agent': AGENT, 'Accept-Encoding': 'identity'}, timeout=30) as client:
    def fetch_range(selection, maximum):
        with client.stream('GET', URL, headers={'Range': selection}) as response:
            if response.status_code != 206:
                raise ValueError(f'expected partial response, got {response.status_code}')
            payload = bytearray()
            for chunk in response.iter_bytes():
                payload.extend(chunk)
                if len(payload) > maximum:
                    raise ValueError('range response exceeds bound')
            requests.append({'range': selection, 'content_range': response.headers.get('content-range'), 'bytes': len(payload)})
            return bytes(payload)

    tail = fetch_range('bytes=-65557', 65557)
    position = tail.rfind(b'PK\x05\x06')
    if position < 0:
        raise ValueError('ZIP end record missing')
    end = struct.unpack_from('<4s4H2LH', tail, position)
    if end[1] != 0 or end[2] != 0 or end[3] != end[4]:
        raise ValueError('multipart ZIP unsupported')
    size, offset, comment = end[5], end[6], end[7]
    if size > 2 * 1024 * 1024:
        raise ValueError('central directory too large')
    central = fetch_range(f'bytes={offset}-{offset + size - 1}', size)
    patched = struct.pack('<4s4H2LH', *end[:6], 0, comment) + tail[position + 22:position + 22 + comment]
    archive = zipfile.ZipFile(io.BytesIO(central + patched))
    choices = [info for info in archive.infolist() if re.search(r'_A201_', info.filename, re.I) and info.filename.lower().endswith('.csv')]
    if len(choices) != 1:
        raise ValueError(f'expected exactly one A201 entry, found {len(choices)}')
    info = choices[0]
    if info.flag_bits & 1 or info.file_size > 32 * 1024 * 1024 or info.compress_size > 8 * 1024 * 1024:
        raise ValueError('station entry is encrypted or exceeds bounds')
    header = fetch_range(f'bytes={info.header_offset}-{info.header_offset + 29}', 30)
    local = struct.unpack('<4s5H3L2H', header)
    if local[0] != b'PK\x03\x04':
        raise ValueError('local header signature invalid')
    start = info.header_offset + 30 + local[-2] + local[-1]
    compressed = fetch_range(f'bytes={start}-{start + info.compress_size - 1}', info.compress_size)
    if info.compress_type == zipfile.ZIP_DEFLATED:
        decoder = zlib.decompressobj(-15)
        raw = decoder.decompress(compressed, info.file_size + 1)
        if not decoder.eof or decoder.unused_data:
            raise ValueError('invalid compressed stream')
    elif info.compress_type == zipfile.ZIP_STORED:
        raw = compressed
    else:
        raise ValueError('compression method unsupported')
    if len(raw) != info.file_size or binascii.crc32(raw) != info.CRC:
        raise ValueError('station entry size or CRC mismatch')
    output = root / 'A201-2025.csv'
    with output.open('xb') as handle:
        handle.write(raw)
    catalogue_url = 'https://apitempo.inmet.gov.br/estacoes/T'
    response = client.get(catalogue_url)
    response.raise_for_status()
    stations = [station for station in response.json() if station.get('CD_ESTACAO') == 'A201']
    if len(stations) != 1:
        raise ValueError('A201 missing or ambiguous in official catalogue')
    report = {'source_url': URL, 'zip_entry': info.filename, 'csv_sha256': hashlib.sha256(raw).hexdigest(), 'csv_bytes': len(raw), 'crc32_verified': True, 'range_requests': requests, 'downloaded_zip_bytes': sum(row['bytes'] for row in requests), 'catalogue_url': catalogue_url, 'station': stations[0], 'tls_verification': True}
    Path('docs/planejamento/reference-candidate-1/evidence/obtencao-inmet-a201.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
