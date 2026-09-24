from tests.integration.api.test_risk_endpoint import app_for, valid_query


async def test_proxy_keeps_individual_quotas_and_ignores_forged_prefix() -> None:
    async with app_for(trusted_proxy_ips=("10.0.0.2",), peer=("10.0.0.2", 443)) as (
        client,
        _,
        _,
        _,
    ):
        responses = [
            await client.get(
                "/api/v1/risk", params=valid_query(), headers={"X-Forwarded-For": "198.51.100.7"}
            )
            for _ in range(10)
        ]
        blocked = await client.get(
            "/api/v1/risk",
            params=valid_query(),
            headers={"X-Forwarded-For": "203.0.113.66, 198.51.100.7"},
        )
        second = await client.get(
            "/api/v1/risk", params=valid_query(), headers={"X-Forwarded-For": "198.51.100.8"}
        )
    assert all(response.status_code == 200 for response in responses)
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert blocked.headers["retry-after"] == "1"
    assert second.status_code == 200
