import asyncio
from time import perf_counter
from typing import List
from fastapi import APIRouter, Depends
from fastapi.params import Body, Query
import operator

from api.filter_keywords import filter_keywords
from api.find_unique_lines import find_unique_lines
from api.get_keyword_wiki_scores import get_keyword_wiki_scores
from api.event_handler import emitter
from api.models.keyword import Keyword
from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)
from api.generate_keywords import generate_keywords
from ..dependencies import require_auth_token

router = APIRouter(
    tags=["keywords"],
    dependencies=[Depends(require_auth_token)],
    responses={403: {"description": "Not authorized"}},
)


@router.put(
    "/keywords",
    response_model=List[Keyword],
    response_description="A list of keywords with metadata",
)
async def add_keywords(
    words: str = Body(
        "we are keywords",
        description="New keywords added by user",
        min_length=1,
    ),
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    # Run lines through Spacy to obtain keywords and categorize them according to their POS
    start = perf_counter()
    keywords = await generate_keywords(words, identifier)
    print(f"{perf_counter() - start: 0.4f} for all")
    # keywords = await verify_words_with_wordsAPI(keywords)
    # keywords = get_keyword_wiki_scores(keywords)
    # keywords = await filter_keywords(keywords, identifier)

    keywords.sort(key=operator.attrgetter("keyword"))
    keywords.sort(key=operator.attrgetter("keyword_total_score"), reverse=True)

    # makes mongo upsert asynchronous and emits names afterwards
    async def persist_keywords_n_send_names():
        await UserPreferenceMutations.upsert_multiple_keywords_in_greylist(keywords, identifier)
        emitter.emit("generate_names", identifier)

    loop = asyncio.get_event_loop()
    loop.create_task(persist_keywords_n_send_names())

    return keywords


@router.get(
    "/keywords",
    response_model=List[Keyword],
    response_description="A list of keywords with metadata",
)
async def get_keywords(
    identifier: str = Query(
        ..., description="Websocket identifier of client (delivered at login)"
    ),
):
    words = await UserPreferenceMutations.get_greylisted(identifier)
    return words
