from fastapi import APIRouter, Depends

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