"""Validate that the frontend uses the privacy-preserving risk POST contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check() -> None:
    api = (ROOT / "frontend/api.js").read_text(encoding="utf-8")
    index = (ROOT / "frontend/index.html").read_text(encoding="utf-8")

    assert "export function queryPayload(formData)" in api
    assert "method: 'POST'" in api
    assert "Content-Type': 'application/json'" in api
    assert "body: JSON.stringify(queryPayload(formData))" in api
    assert "`/api/v1/risk?" not in api
    assert 'action="/api/v1/risk" method="post"' in index


if __name__ == "__main__":
    check()
    print("Frontend risk POST contract: OK.")
