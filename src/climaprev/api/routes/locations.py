from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from climaprev.api.deps import enforce_rate_limit, get_location_search
from climaprev.application.ports import LocationSearchPort

router = APIRouter(prefix="/api/v1", tags=["locations"])


class LocationCandidateResponse(BaseModel):
    name: str
    latitude: float
    longitude: float
    timezone: str
    source: str


@router.get(
    "/locations/search",
    response_model=list[LocationCandidateResponse],
    dependencies=[Depends(enforce_rate_limit)],
)
async def search_locations(
    query: Annotated[str, Query(min_length=2, max_length=100)],
    search: Annotated[LocationSearchPort, Depends(get_location_search)],
) -> list[LocationCandidateResponse]:
    candidates = await search.search(query.strip())
    return [
        LocationCandidateResponse(
            name=location.name,
            latitude=location.latitude,
            longitude=location.longitude,
            timezone=location.timezone,
            source=location.source,
        )
        for location in candidates[:5]
    ]
