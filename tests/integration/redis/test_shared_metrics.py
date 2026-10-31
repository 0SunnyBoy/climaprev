import os
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from climaprev.api.observability import RequestMetrics
from climaprev.infrastructure.metrics_store import MetricsStore, prometheus_text


@pytest.mark.asyncio
async def test_two_workers_export_counters_histograms_and_expire_without_percentile_averaging():
    redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    now = [100.0]
    environment = f"metrics-{uuid4().hex}"
    store = MetricsStore(redis, environment, clock=lambda: now[0])
    try:
        workers = [RequestMetrics(), RequestMetrics()]
        for index, worker in enumerate(workers):
            worker.record_request(route="/api/v1/risk", status_code=200,
                                  duration_seconds=index + 0.1, cache="hit", error_code=None)
            await store.publish(worker)
        report = await store.read()
        assert report["active_workers"] == 2
        assert all("request_latency_ms" not in data for data in report["workers"])
        exported = prometheus_text(report)
        assert exported.count('route="/api/v1/risk"') == 2
        assert 'le="+Inf"} 1' in exported
        assert "histogram" in exported
        assert sum(data["http_request_duration_seconds"]["count"] for data in report["workers"]) == 2
        now[0] += 21
        assert (await store.read())["active_workers"] == 0
        await store.publish(workers[0])
        assert (await store.read())["active_workers"] == 1
        assert await redis.zcard(f"{store.prefix}:registry") == 1
    finally:
        for key in await redis.keys(f"{store.prefix}:*"):
            await redis.delete(key)
        await redis.aclose()
