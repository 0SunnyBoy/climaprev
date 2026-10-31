"""Bounded D7 transport and immutable raw/derived archives, independent of the pilot."""

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, cast
from zoneinfo import ZoneInfo

import httpx

from climaprev.tools.historical_experiment import digest, read_json

ENDPOINT = "https://api.open-meteo.com/v1/forecast"
MAX_BYTES = 4 * 1024 * 1024


def _aware(value: datetime) -> datetime:
    if value.utcoffset() is None:
        raise ValueError("aware clock required")
    return value.astimezone(UTC)


def _adapter_view(payload: dict[str, Any], target: date, zone: ZoneInfo) -> dict[str, Any]:
    """Explicit derived representation; raw epoch JSON remains byte-for-byte separate."""
    if payload.get("timezone") != zone.key:
        raise ValueError("returned timezone differs from frozen station")
    result = dict(payload)
    for section in ("daily", "hourly"):
        source = payload[section]
        stamps = source["time"]
        if (not isinstance(stamps, list) or any(isinstance(t, bool) or not isinstance(t, int) for t in stamps)
                or stamps != sorted(set(stamps))):
            raise ValueError("epoch timestamps must be unique and increasing")
        local = [datetime.fromtimestamp(t, UTC).astimezone(zone) for t in stamps]
        selected = [i for i, t in enumerate(local) if t.date() == target]
        filtered = {}
        for key, values in source.items():
            if not isinstance(values, list) or len(values) != len(stamps):
                raise ValueError("provider series must align with timestamps")
            filtered[key] = [values[i] for i in selected]
        filtered["time"] = [(local[i].date().isoformat() if section == "daily"
                             else local[i].replace(tzinfo=None).isoformat(timespec="minutes")) for i in selected]
        result[section] = filtered
    return result


def write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as stream:
            stream.write(data)
    except FileExistsError:
        if path.read_bytes() != data:
            raise ValueError("refusing to overwrite divergent archive") from None


class ControlTransport(httpx.AsyncBaseTransport):
    def __init__(
        self, client: httpx.AsyncClient, job: dict[str, Any], directory: Path,
        before_send: Callable[[], None], clock: Callable[[], datetime],
    ) -> None:
        self.client, self.job, self.directory = client, job, directory
        self.before_send, self.clock = before_send, clock
        self.record: dict[str, Any] = {}
        self.payload: dict[str, Any] | None = None

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if str(request.url.copy_with(query=None)) != ENDPOINT or self.record:
            raise ValueError("one bounded standard-provider request per job required")
        target = date.fromisoformat(self.job["target_date"])
        # Extend only the transport window, preserving the target adapter/policy view.
        url = request.url.copy_set_param("end_date", (target + timedelta(days=1)).isoformat())
        url = url.copy_set_param("timeformat", "unixtime")
        url = url.copy_set_param("timezone", self.job["station"]["timezone"])
        self.before_send()
        self.record = {"adapter_request_parameters": dict(request.url.params),
                       "actual_request_parameters": dict(url.params), "endpoint": ENDPOINT,
                       "sent_at": _aware(self.clock()).isoformat(),
                       "body_representation": "decoded_http_entity_bytes_not_reserialized_json"}
        body = bytearray()
        async with self.client.stream("GET", url, follow_redirects=False, timeout=15) as response:
            self.record["http_status"] = response.status_code
            async for chunk in response.aiter_bytes():
                if len(body) + len(chunk) > MAX_BYTES:
                    raise ValueError("raw response exceeds size limit")
                body.extend(chunk)
        raw = bytes(body)
        name = hashlib.sha256(raw).hexdigest() + ".body"
        write_once(self.directory / name, raw)
        self.record.update({"received_at": _aware(self.clock()).isoformat(),
                            "raw_file": name, "raw_sha256": name.removesuffix(".body"),
                            "raw_size": len(raw)})
        if response.status_code != 200:
            return httpx.Response(response.status_code, content=raw)
        self.payload = json.loads(raw)
        if not isinstance(self.payload, dict):
            raise TypeError("provider response must be an object")
        derived = _adapter_view(self.payload, target, ZoneInfo(self.job["station"]["timezone"]))
        self.record["adapter_view_sha256"] = digest(derived)
        return httpx.Response(200, json=derived)


def load_control_archive(path: Path) -> dict[str, Any]:
    """Detect content or raw-body corruption; hashes do not authenticate the provider."""
    envelope = read_json(path)
    data = envelope["capture"]
    if envelope["sha256"] != digest(data) or path.stem != envelope["sha256"]:
        raise ValueError("D7 capture identity differs")
    record = data["request"]
    if record.get("raw_file"):
        name = record["raw_file"]
        if name != record["raw_sha256"] + ".body" or Path(name).name != name:
            raise ValueError("invalid raw archive path")
        raw = (path.parent / name).read_bytes()
        if len(raw) != record["raw_size"] or hashlib.sha256(raw).hexdigest() != record["raw_sha256"]:
            raise ValueError("raw response integrity differs")
    return cast(dict[str, Any], data)
