"""HTTP/static acceptance gate for the public frontend boundary.

The production image remains free of test dependencies. With ``--base-url`` this
also checks a running local or TLS entrance. Browser automation can reuse the
same assertions from a pinned Playwright runner in CI.
"""

import argparse
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ("/assets/styles.css", "/assets/app.js", "/assets/api.js", "/assets/result.js")


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
    scripts = "\n".join((ROOT / f"frontend/{name}").read_text(encoding="utf-8") for name in ("app.js", "api.js", "result.js"))
    assert "fetch('/api/v1/risk'" in scripts
    assert "/api/v1/locations/search?query=" in scripts
    assert "innerHTML" not in scripts
    assert "document.write" not in scripts
    assert "eval(" not in scripts and "new Function(" not in scripts
    assert "textContent" in scripts
    assert not re.search(r"(?:password|secret|api[_-]?key|token)\s*[:=]", index + "\n" + scripts, re.IGNORECASE)
    assert "http://" not in scripts and "https://" not in scripts
    synthetic = "<img src=x onerror=alert('SYNTHETIC-XSS')>"
    assert synthetic not in index + scripts
    assert json.loads(json.dumps({"name": synthetic}))["name"].startswith("<img")


def check_http(base_url: str) -> None:
    root = base_url.rstrip("/")
    status, body, content_type = _request(root + "/")
    assert status == 200 and content_type == "text/html" and "<title>" in body
    for path in ASSETS:
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
