from fastapi import APIRouter, Depends
from fastapi.param_functions import Query

from ..dependencies import require_auth_token
from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)

router = APIRouter(
    tags=["settings"],
    dependencies=[Depends(require_auth_token)],
    responses={403: {"description": "Not authorized"}},
)

@router.get("/profile")
async def get_profile(username: str):
    return await UserPreferenceMutations.get_profile(username)

@router.delete("/preferences")
async def delete_prefs(identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    )):
    await UserPreferenceMutations._drop_blacklist(identifier)
    await UserPreferenceMutations._drop_greylist(identifier)
    await UserPreferenceMutations._drop_whitelist(identifier)
    await UserPreferenceMutations._drop_algorithms(identifier)
