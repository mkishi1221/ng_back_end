from typing import List
import orjson as json
from fastapi import APIRouter, Depends, Response, status
from fastapi.params import Query

from api.models.keyword import Keyword
from api.models.tld import TLD
from ..dependencies import require_auth_token
from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)

router = APIRouter(
    tags=["preferences"],
    dependencies=[Depends(require_auth_token)],
    responses={403: {"description": "Not authorized"}},
)


@router.get("/tlds")
async def get_tlds(
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    return await UserPreferenceMutations.get_tlds(identifier)


@router.put(
    "/tlds",
    response_model=List[TLD],
    response_description="A list of algorithm objects",
)
async def add_tld(
    tld: TLD,
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    result = await UserPreferenceMutations.upsert_tld(tld, identifier)
    return result


@router.delete("/tld/{tld}")
async def remove_tld(
    tld: str,
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    removed = TLD.schema().loads(
        json.dumps(await UserPreferenceMutations.remove_from_tlds(tld, identifier))
    )
    return removed
