from typing import List
from fastapi import APIRouter, Depends
from fastapi.params import Body, Query
import operator

from api.filter_keywords import filter_keywords
from api.find_unique_lines import find_unique_lines
from api.get_keyword_wiki_scores import get_keyword_wiki_scores
from api.models.keyword import Keyword
from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)
from api.word_api import verify_words_with_wordsAPI
from api.extract_words_with_spacy import extract_words_with_spacy
from ..dependencies import require_auth_token
from ..event_handler import emitter

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
    unique_lines = find_unique_lines(words)
    # Run lines through Spacy to obtain keywords and categorize them according to their POS
    keywords = extract_words_with_spacy(unique_lines)
    keywords = verify_words_with_wordsAPI(keywords)
    keywords = get_keyword_wiki_scores(keywords)
    keywords = filter_keywords(keywords, identifier)

    keywords.sort(key=operator.attrgetter("keyword"))
    keywords.sort(key=operator.attrgetter("keyword_total_score"), reverse=True)

    UserPreferenceMutations.upsert_multiple_keywords_in_greylist(keywords, identifier)

    emitter.emit("generate_names", identifier)

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
    words = UserPreferenceMutations.get_greylisted(identifier)
    return words
