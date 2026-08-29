from dataclasses import dataclass
from typing import Literal

from climaprev.domain.models import CanonicalLocation, DatePeriod, OfficialAlert


@dataclass(frozen=True, slots=True)
class OfficialAlertsNotConfiguredProvider:
    status: Literal["not_configured"] = "not_configured"

    async def get_alerts(
        self,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> list[OfficialAlert]:
        return []
