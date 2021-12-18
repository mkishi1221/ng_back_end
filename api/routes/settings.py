from fastapi import APIRouter, Depends
from fastapi.param_functions import Query

from ..dependencies import require_auth_token
from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)
from ..event_handler import ConnectionManager, emitter


router = APIRouter(
    tags=["settings"],
    dependencies=[Depends(require_auth_token)],
    responses={403: {"description": "Not authorized"}},
)

@router.get("/profile")
async def get_profile(username: str):
    return UserPreferenceMutations.get_profile(username)

@router.delete("/preferences")
async def delete_prefs(identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    )):
    UserPreferenceMutations._drop_blacklist(identifier)
    UserPreferenceMutations._drop_greylist(identifier)
    UserPreferenceMutations._drop_whitelist(identifier)
    UserPreferenceMutations._drop_algorithms(identifier)
