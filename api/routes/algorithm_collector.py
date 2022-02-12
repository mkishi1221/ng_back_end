from typing import List
from fastapi import APIRouter, Depends
from fastapi.params import Query

from ..dependencies import require_auth_token
from api.models.algorithm import Algorithm
from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)
from ..event_handler import emitter


router = APIRouter(
    tags=["algorithms"],
    dependencies=[Depends(require_auth_token)],
    responses={403: {"description": "Not authorized"}},
)


@router.get(
    "/algorithms",
    response_model=List[Algorithm],
    response_description="A list of algorithm objects",
)
async def get_algorithms(
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    return UserPreferenceMutations.get_algorithms(identifier)


@router.put(
    "/algorithms",
    response_model=List[Algorithm],
    response_description="A list of algorithm objects",
)
async def add_algorithm(
    algorithm: Algorithm,
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    result = UserPreferenceMutations.upsert_algorithm(algorithm, identifier)
    emitter.emit("generate_names", identifier)
    return result


@router.delete("/algorithms/{id}")
async def delete_algorithm(
    id: str,
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    result = UserPreferenceMutations.remove_from_algorithms(id, identifier)
    emitter.emit("generate_names", identifier)
    return result


@router.delete("/algorithms")
async def delete_all_algorithms(
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    result = UserPreferenceMutations._drop_algorithms(identifier)
    return result
