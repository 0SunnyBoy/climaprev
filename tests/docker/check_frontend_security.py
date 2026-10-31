"""HTTP/static acceptance gate for the public Vue frontend boundary."""

import argparse
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _request(url: str) -> tuple[int, str, str]:
    request = urllib.request.Request(url, headers={"Accept": "text/html, application/javascript, text/css"})
    try:
        response = urllib.request.urlopen(request, timeout=5)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.status, response.read().decode("utf-8"), response.headers.get_content_type()


def check_static() -> None:
    index = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
    source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "frontend/src").rglob("*.ts")
                       if not path.name.endswith(".test.ts"))
    source += "\n" + "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "frontend/src").rglob("*.vue"))
    assert "fetch(apiUrl('/api/v1/risk')" in source
    assert "/api/v1/locations/search?query=" in source
    assert "innerHTML" not in source
    assert "document.write" not in source
    assert "eval(" not in source and "new Function(" not in source
    assert "textContent" not in source
    assert not re.search(r"(?:password|secret|api[_-]?key|token)\s*[:=]", index + "\n" + source, re.IGNORECASE)
    assert "http://" not in source and "https://" not in source
    synthetic = "<img src=x onerror=alert('SYNTHETIC-XSS')>"
    assert synthetic not in index + source
    assert json.loads(json.dumps({"name": synthetic}))["name"].startswith("<img")


def check_http(base_url: str) -> None:
    root = base_url.rstrip("/")
    status, body, content_type = _request(root + "/")
    assert status == 200 and content_type == "text/html" and "<title>" in body
    assets = re.findall(r"(?:href|src)=\"(/assets/[^\"]+)\"", body)
    assert any(asset.endswith(".css") for asset in assets)
    assert any(asset.endswith(".js") for asset in assets)
    for path in assets:
        status, body, content_type = _request(root + path)
        assert status == 200 and body
        assert content_type in {"text/css", "application/javascript"}
    for path in ("/.env", "/.git/config", "/docs", "/internal/metrics"):
        status, body, _ = _request(root + path)
        assert status == 404 and "SYNTHETIC" not in body


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url")
    args = parser.parse_args()
    check_static()
    if args.base_url:
        check_http(args.base_url)
    print("Frontend security acceptance contract: OK.")
