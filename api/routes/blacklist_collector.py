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


@router.post("/blacklist")
async def add_keyword_to_blacklist(
    keyword: Keyword,
    identifier: str = Query(
        None, description="Websocket identifier of client (delivered at login)"
    ),
):
    UserPreferenceMutations.upsert_keyword_in_blacklist(keyword)
    emitter.emit("new_words", identifier)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
