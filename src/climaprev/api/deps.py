from __future__ import annotations

import ipaddress
from typing import Annotated, cast

from fastapi import Depends, Request

from climaprev.api.errors import RateLimitExceeded
from climaprev.application.ports import LocationSearchPort, RateLimiterPort
from climaprev.application.services.forecast_query import ForecastQueryPort
from climaprev.config import Settings

_MAX_FORWARDED_FOR_ENTRIES = 20


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def get_forecast_query_service(request: Request) -> ForecastQueryPort:
    return cast(ForecastQueryPort, request.app.state.forecast_query_service)


def get_location_search(request: Request) -> LocationSearchPort:
    return cast(LocationSearchPort, request.app.state.location_search)


def get_rate_limiter(request: Request) -> RateLimiterPort:
    return cast(RateLimiterPort, request.app.state.rate_limiter)


def client_identity(request: Request, settings: Settings) -> str:
    peer_ip = _canonical_ip(request.client.host) if request.client is not None else None
    peer = peer_ip or "unknown"
    if peer_ip is None or peer_ip not in settings.trusted_proxy_ips:
        return peer

    forwarded_for = request.headers.get("x-forwarded-for")
    if not forwarded_for:
        return peer
    raw_chain = [address.strip() for address in forwarded_for.split(",")]
    if not raw_chain or len(raw_chain) > _MAX_FORWARDED_FOR_ENTRIES:
        return peer
    chain = [_canonical_ip(address) for address in raw_chain]
    if any(address is None for address in chain):
        return peer
    addresses = [address for address in chain if address is not None]
    # The peer is the implicit trusted final hop. Walk XFF right-to-left and
    # use the first non-trusted address as the client; earlier values can be
    # user-supplied and must not affect the identity.
    for address in reversed(addresses):
        if address not in settings.trusted_proxy_ips:
            return address
    return peer


def _canonical_ip(value: str) -> str | None:
    try:
        if "%" in value:
            return None
        return str(ipaddress.ip_address(value))
    except ValueError:
        return None


async def enforce_rate_limit(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    rate_limiter: Annotated[RateLimiterPort, Depends(get_rate_limiter)],
) -> None:
    decision = await rate_limiter.allow(
        client_identity(request, settings),
        limit=settings.rate_limit,
        window_seconds=settings.rate_limit_window_seconds,
        burst=settings.rate_limit_burst,
    )
    if not decision.allowed:
        request.app.state.metrics.record_rate_limit_rejection()
        raise RateLimitExceeded(decision.retry_after_seconds)
