from __future__ import annotations

import json
from collections.abc import Awaitable, Callable, Mapping, Sequence
from datetime import datetime, time, timedelta
from itertools import pairwise
from math import isfinite
from typing import Final
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx

from climaprev.application.errors import WeatherDataInvalid
from climaprev.config import Settings
from climaprev.domain.models import CanonicalLocation, DatePeriod, OfficialAlert
from climaprev.infrastructure.http.client import AsyncJsonHttpClient

_INMET_ZONE: Final = "America/Sao_Paulo"
_ALERT_DATE_FORMATS: Final = ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S")

__all__ = ["InmetOfficialAlertsProvider"]


class InmetOfficialAlertsProvider:
    provider_identity = "inmet-alerts-v2"

    def __init__(
        self,
        client: httpx.AsyncClient,
        settings: Settings,
        *,
        on_retry: Callable[[], None] | None = None,
        before_send: Callable[[str], Awaitable[None]] | None = None,
    ) -> None:
        self._http = AsyncJsonHttpClient(
            client, settings, on_retry=on_retry, before_send=before_send,
            headers={
                "User-Agent": "ClimaPrev/0.1.0 (+https://github.com/0SunnyBoy/climaprev)",
                "Accept": "application/json",
            },
        )
        self._base_url = settings.inmet_alerts_base_url.rstrip("/")
        try:
            self._zone = ZoneInfo(_INMET_ZONE)
        except ZoneInfoNotFoundError as error:
            raise RuntimeError("INMET timezone data is unavailable") from error

    async def get_alerts(
        self,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> list[OfficialAlert]:
        payload = await self._http.get_json(f"{self._base_url}/avisos/ativos", {})
        records = _records(payload)
        try:
            location_zone = ZoneInfo(location.timezone)
        except (ValueError, ZoneInfoNotFoundError) as error:
            raise WeatherDataInvalid("location timezone is invalid for alert coverage") from error
        requested_start = datetime.combine(period.start, time.min, location_zone)
        requested_end = datetime.combine(
            period.end + timedelta(days=1), time.min, location_zone
        )
        alerts: list[OfficialAlert] = []
        for record in records:
            alert = _official_alert(record, location, requested_start, requested_end, self._zone)
            if alert is not None:
                alerts.append(alert)
        return alerts


def _records(payload: Mapping[str, object]) -> list[Mapping[str, object]]:
    records: list[Mapping[str, object]] = []
    for bucket_name in ("hoje", "futuro"):
        bucket = payload.get(bucket_name)
        if not isinstance(bucket, list):
            raise WeatherDataInvalid(f"INMET {bucket_name} must be a list")
        for item in bucket:
            if not isinstance(item, Mapping):
                raise WeatherDataInvalid("INMET alert record must be an object")
            records.append(item)
    return records


def _official_alert(
    record: Mapping[str, object],
    location: CanonicalLocation,
    requested_start: datetime,
    requested_end: datetime,
    zone: ZoneInfo,
) -> OfficialAlert | None:
    effective_at = _alert_datetime(record.get("inicio") or record.get("data_inicio"), zone)
    expires_at = _alert_datetime(record.get("fim") or record.get("data_fim"), zone)
    if effective_at is None or expires_at is None or expires_at <= effective_at:
        raise WeatherDataInvalid("INMET alert validity is missing or invalid")
    polygons = _geometry(record.get("poligono"))
    if not any(_contains(location.longitude, location.latitude, polygon) for polygon in polygons):
        return None
    if effective_at >= requested_end or expires_at <= requested_start:
        return None

    identifier = _identifier(record.get("id"))
    return OfficialAlert(
        source="INMET",
        event=_string(record.get("descricao")) or "Aviso meteorológico",
        severity=_string(record.get("severidade")) or "Não informada",
        effective_at=effective_at,
        expires_at=expires_at,
        geographic_scope=_scope(record),
        source_url=f"https://avisos.inmet.gov.br/{identifier}" if identifier else None,
    )


def _alert_datetime(value: object, zone: ZoneInfo) -> datetime | None:
    if not isinstance(value, str):
        return None
    for date_format in _ALERT_DATE_FORMATS:
        try:
            return datetime.strptime(value, date_format).replace(tzinfo=zone)
        except ValueError:
            continue
    return None


def _scope(record: Mapping[str, object]) -> str:
    for field in ("regioes", "estados", "municipios"):
        value = _string(record.get(field))
        if value:
            return value
    return "Área definida pelo INMET"


Ring = tuple[tuple[float, float], ...]
Polygon = tuple[Ring, ...]


def _geometry(value: object) -> tuple[Polygon, ...]:
    if not isinstance(value, str) or not value.strip():
        raise WeatherDataInvalid("INMET geometry is missing")
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        raise WeatherDataInvalid("INMET geometry is invalid JSON") from None
    if not isinstance(parsed, Mapping) or parsed.get("type") not in {"Polygon", "MultiPolygon"}:
        raise WeatherDataInvalid("INMET geometry must be Polygon or MultiPolygon")
    coordinates = parsed.get("coordinates")
    if not isinstance(coordinates, list) or not coordinates:
        raise WeatherDataInvalid("INMET geometry has no coordinates")
    raw_polygons = [coordinates] if parsed["type"] == "Polygon" else coordinates
    polygons = []
    for polygon in raw_polygons:
        if not isinstance(polygon, list) or not polygon:
            raise WeatherDataInvalid("INMET polygon has no rings")
        polygons.append(tuple(_ring(ring) for ring in polygon))
    return tuple(polygons)


def _ring(ring: object) -> Ring:
    if not isinstance(ring, list) or len(ring) < 4:
        raise WeatherDataInvalid("INMET ring requires at least four positions")
    points: list[tuple[float, float]] = []
    for point in ring:
        if (
            not isinstance(point, list)
            or len(point) < 2
            or isinstance(point[0], bool)
            or isinstance(point[1], bool)
            or not isinstance(point[0], int | float)
            or not isinstance(point[1], int | float)
        ):
            raise WeatherDataInvalid("INMET position must contain numeric longitude/latitude")
        if not isfinite(point[0]) or not isfinite(point[1]) or not (
            -180 <= point[0] <= 180 and -90 <= point[1] <= 90
        ):
            raise WeatherDataInvalid("INMET position is outside valid WGS84 bounds")
        points.append((float(point[0]), float(point[1])))
    if points[0] != points[-1] or len(set(points)) < 3:
        raise WeatherDataInvalid("INMET ring must be closed and non-degenerate")
    if any(abs(left[0] - right[0]) > 180 for left, right in pairwise(points)):
        raise WeatherDataInvalid("antimeridian-crossing INMET ring is unsupported")
    area = sum(left[0] * right[1] - right[0] * left[1] for left, right in pairwise(points))
    if abs(area) <= 1e-12:
        raise WeatherDataInvalid("INMET ring has zero signed area")
    return tuple(points)


def _contains(longitude: float, latitude: float, polygon: Polygon) -> bool:
    if not _point_in_polygon(longitude, latitude, polygon[0]):
        return False
    # A point on a hole boundary is conservatively included in the warning area.
    for hole in polygon[1:]:
        if any(_point_on_segment(longitude, latitude, *left, *right)
               for left, right in pairwise(hole)):
            return True
        if _point_in_polygon(longitude, latitude, hole):
            return False
    return True


def _point_in_polygon(
    longitude: float,
    latitude: float,
    polygon: Sequence[tuple[float, float]],
) -> bool:
    inside = False
    previous_longitude, previous_latitude = polygon[-1]
    for current_longitude, current_latitude in polygon:
        if _point_on_segment(
            longitude,
            latitude,
            previous_longitude,
            previous_latitude,
            current_longitude,
            current_latitude,
        ):
            return True
        crosses_latitude = (current_latitude > latitude) != (previous_latitude > latitude)
        if crosses_latitude:
            intersection = (
                (previous_longitude - current_longitude)
                * (latitude - current_latitude)
                / (previous_latitude - current_latitude)
                + current_longitude
            )
            if longitude < intersection:
                inside = not inside
        previous_longitude, previous_latitude = current_longitude, current_latitude
    return inside


def _point_on_segment(
    longitude: float,
    latitude: float,
    first_longitude: float,
    first_latitude: float,
    second_longitude: float,
    second_latitude: float,
) -> bool:
    cross = (longitude - first_longitude) * (second_latitude - first_latitude) - (
        latitude - first_latitude
    ) * (second_longitude - first_longitude)
    if abs(cross) > 1e-9:
        return False
    return (
        min(first_longitude, second_longitude) - 1e-9
        <= longitude
        <= max(first_longitude, second_longitude) + 1e-9
        and min(first_latitude, second_latitude) - 1e-9
        <= latitude
        <= max(first_latitude, second_latitude) + 1e-9
    )


def _string(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def _identifier(value: object) -> str | None:
    if isinstance(value, bool) or not isinstance(value, int | str):
        return None
    identifier = str(value).strip()
    return identifier or None
