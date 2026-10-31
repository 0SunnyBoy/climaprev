"""Resolve user input to a canonical location with geocoding cache."""

from urllib.parse import quote

from climaprev.application.cache_codec import decode_location, encode_location
from climaprev.application.ports import CacheEntry, CachePort, GeocodingPort
from climaprev.application.query import ForecastQuery
from climaprev.domain.models import CanonicalLocation

_GEO_CACHE_TTL_SECONDS = 24 * 60 * 60


class CachedLocationResolver:
    def __init__(self, geocoder: GeocodingPort, cache: CachePort) -> None:
        self._geocoder = geocoder
        self._cache = cache

    async def resolve(self, query: ForecastQuery) -> CanonicalLocation:
        if query.location_text is None:
            if query.latitude is None or query.longitude is None:
                raise ValueError("validated query must include a location")
            return CanonicalLocation(
                name=f"{query.latitude:.4f},{query.longitude:.4f}",
                latitude=query.latitude,
                longitude=query.longitude,
                timezone="UTC",
                source="coordinates",
            )

        key = _geo_key(query.location_text)
        cached = await self._cache.get(key)
        if cached is not None:
            location = decode_location(cached.value)
            if location is not None:
                return location

        location = await self._geocoder.resolve(query.location_text)
        await self._cache.set(
            key,
            CacheEntry(value=encode_location(location), is_stale=False),
            fresh_ttl_seconds=_GEO_CACHE_TTL_SECONDS,
            stale_ttl_seconds=_GEO_CACHE_TTL_SECONDS,
        )
        return location



def _geo_key(location_text: str) -> str:
    return f"geo:v1:{quote(location_text.casefold(), safe='')}"
