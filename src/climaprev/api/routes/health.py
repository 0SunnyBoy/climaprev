"""Liveness and dependency readiness routes."""

from fastapi import FastAPI, Request
from redis.exceptions import RedisError

from climaprev.application.errors import DependencyUnavailable


def register_health_routes(app: FastAPI) -> None:
    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "live"}

    @app.get("/health/ready")
    async def ready(request: Request) -> dict[str, str]:
        try:
            available = await request.app.state.redis.ping()
        except RedisError as error:
            request.app.state.metrics.record_dependency_circuit_state("redis", "open")
            raise DependencyUnavailable from error
        if available is not True:
            request.app.state.metrics.record_dependency_circuit_state("redis", "open")
            raise DependencyUnavailable
        request.app.state.metrics.record_dependency_circuit_state("redis", "closed")
        return {"status": "ready"}
