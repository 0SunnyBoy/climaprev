from __future__ import annotations

from collections.abc import Mapping
from uuid import uuid4

from locust import HttpUser, constant_throughput, task

from tests.load.scenarios import per_user_request_rate, request_parameters, selected_scenario

REQUESTS_PER_SECOND_PER_USER = per_user_request_rate()


class RiskApiUser(HttpUser):
    wait_time = constant_throughput(REQUESTS_PER_SECOND_PER_USER)

    def on_start(self) -> None:
        self._scenario = selected_scenario()
        self._user_id = uuid4().hex
        self._sequence = 0
        if self._scenario == "warm_cache":
            self._fetch(sequence=0, name="/api/v1/risk [warm_cache prime]")

    @task
    def fetch_risk(self) -> None:
        self._fetch(sequence=self._sequence, name=f"/api/v1/risk [{self._scenario}]")
        self._sequence += 1

    def _fetch(self, *, sequence: int, name: str) -> None:
        params = request_parameters(self._scenario, sequence, user_id=self._user_id)
        headers: Mapping[str, str] = {"X-Load-Scenario": self._scenario}
        with self.client.get(
            "/api/v1/risk",
            params=params,
            headers=headers,
            name=name,
            catch_response=True,
        ) as response:
            if response.status_code == 429:
                response.failure("rate-limit response: configure compatible limits and distinct client IPs")
            elif response.status_code >= 500:
                response.failure(f"server response: {response.status_code}")
            elif response.status_code != 200:
                response.failure(f"unexpected response: {response.status_code}")
