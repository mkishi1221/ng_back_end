import orjson as json
from fastapi import APIRouter, Depends, Response, status
from fastapi.params import Query

from api.models.keyword import Keyword
from ..dependencies import require_auth_token
from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)
from ..event_handler import emitter


router = APIRouter(
    tags=["preferences"],
    dependencies=[Depends(require_auth_token)],
    responses={403: {"description": "Not authorized"}},
)


@router.get("/blacklist")
async def get_blacklisted(
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    return UserPreferenceMutations.get_blacklisted(identifier)


@router.post("/blacklist")
async def add_keyword_to_blacklist(
    keyword: Keyword,
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    UserPreferenceMutations.upsert_keyword_in_blacklist(keyword, identifier)
    UserPreferenceMutations.remove_from_greylist(keyword.word, identifier)
    emitter.emit("generate_names", identifier)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/blacklist/{word}")
async def remove_keyword_from_blacklist(
    word: str,
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    removed = Keyword.schema().loads(json.dumps(UserPreferenceMutations.remove_from_blacklist(word, identifier)))
    UserPreferenceMutations.upsert_keyword_in_greylist(removed, identifier)
    emitter.emit("generate_names", identifier)
    return word
