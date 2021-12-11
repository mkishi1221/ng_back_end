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
    UserPreferenceMutations.remove_from_greylist(keyword.keyword, identifier)
    emitter.emit("new_words", identifier)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
