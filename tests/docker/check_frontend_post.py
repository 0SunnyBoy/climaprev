"""Validate that the Vue frontend uses the privacy-preserving risk POST contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check() -> None:
    api = (ROOT / "frontend/src/services/api.ts").read_text(encoding="utf-8")
    form = (ROOT / "frontend/src/components/QueryForm.vue").read_text(encoding="utf-8")

    assert "fetch('/api/v1/risk'" in api
    assert "method: 'POST'" in api
    assert "'Content-Type': 'application/json'" in api
    assert "body: JSON.stringify(payload)" in api
    assert "`/api/v1/risk?" not in api
    assert 'action="/api/v1/risk"' in form
    assert 'method="post"' in form


if __name__ == "__main__":
    check()
    print("Frontend risk POST contract: OK.")
