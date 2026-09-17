from __future__ import annotations

from starlette.requests import Request

from climaprev.api.deps import client_identity
from climaprev.config import Settings


def _request(peer: str, forwarded_for: str | None = None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if forwarded_for is not None:
        headers.append((b"x-forwarded-for", forwarded_for.encode()))
    return Request({"type": "http", "headers": headers, "client": (peer, 443)})


def test_returns_client_behind_a_single_trusted_proxy() -> None:
    identity = client_identity(
        _request("10.0.0.2", "198.51.100.7"),
        Settings(trusted_proxy_ips=("10.0.0.2",)),
    )

    assert identity == "198.51.100.7"


def test_resolves_the_first_untrusted_hop_from_multiple_trusted_proxies() -> None:
    identity = client_identity(
        _request("10.0.0.2", "2001:db8::7, 10.0.0.1"),
        Settings(trusted_proxy_ips=("10.0.0.1", "10.0.0.2")),
    )

    assert identity == "2001:db8::7"


def test_ignores_forwarded_for_from_an_untrusted_peer() -> None:
    identity = client_identity(
        _request("198.51.100.9", "198.51.100.7, 10.0.0.1"),
        Settings(trusted_proxy_ips=("10.0.0.1",)),
    )

    assert identity == "198.51.100.9"


def test_falls_back_to_peer_for_malformed_forwarded_chain() -> None:
    settings = Settings(trusted_proxy_ips=("10.0.0.1", "10.0.0.2"))

    assert client_identity(_request("10.0.0.2", "198.51.100.7, invalid"), settings) == "10.0.0.2"
    assert (
        client_identity(_request("10.0.0.2", "198.51.100.7, 203.0.113.8"), settings)
        == "203.0.113.8"
    )


def test_uses_first_untrusted_hop_when_a_client_prefix_was_injected() -> None:
    settings = Settings(trusted_proxy_ips=("10.0.0.1", "10.0.0.2"))

    assert (
        client_identity(
            _request("10.0.0.2", "203.0.113.66, 198.51.100.7, 10.0.0.1"),
            settings,
        )
        == "198.51.100.7"
    )


def test_falls_back_to_peer_when_forwarded_chain_exceeds_the_bound() -> None:
    forwarded_for = ", ".join("198.51.100.7" for _ in range(21))

    assert (
        client_identity(
            _request("2001:db8::2", forwarded_for),
            Settings(trusted_proxy_ips=("2001:db8::2",)),
        )
        == "2001:db8::2"
    )
