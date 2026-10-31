"""Reuse bounded official ZIP extraction, preserving all existing 2025 evidence."""
from pathlib import Path

source = Path(__file__).with_name('fetch_inmet_station_2025_original.py').read_text(encoding='utf-8')
for station in ('A201', 'A001', 'A801'):
    destination = Path(f'.historical-reports/inmet/{station}-2024.csv')
    if destination.exists():
        print(f'Preserved existing {destination}')
        continue
    script = source.replace('2025', '2024').replace('A201', station)
    script = script.replace('obtencao-inmet-a201.json',
                            f'obtencao-inmet-{station.lower()}-2024-2026-10-19.json')
    exec(compile(script, f'official-extraction-{station}', 'exec'), {})

