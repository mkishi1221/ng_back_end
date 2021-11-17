from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.params import Body, Query
import operator

from starlette.responses import Response
from api.filter_keywords import filter_keywords
from api.find_unique_lines import find_unique_lines
from api.get_keyword_wiki_scores import get_keyword_wiki_scores
from api.models.keyword import Keyword
from api.word_api import verify_words_with_wordsAPI
from api.extract_words_with_spacy import extract_words_with_spacy
from ..dependencies import require_auth_token
from ..event_handler import emitter
import orjson as json

router = APIRouter(
    dependencies=[Depends(require_auth_token)],
    responses={403: {"description": "Not authorized"}},
)


@router.put(
    "/",
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
        None, description="Websocket identifier of client (delivered at login)"
    ),
):
    unique_lines = find_unique_lines(words)

    # Run lines through Spacy to obtain keywords and categorize them according to their POS
    keywords = extract_words_with_spacy(unique_lines)
    keywords = verify_words_with_wordsAPI(keywords)
    keywords = get_keyword_wiki_scores(keywords)

    keywords = filter_keywords(keywords)

    keywords.sort(key=operator.attrgetter("keyword"))
    keywords.sort(key=operator.attrgetter("keyword_total_score"), reverse=True)

    emitter.emit("new_words", keywords, identifier)

    return json.dumps(keywords, option=json.OPT_SERIALIZE_DATACLASS)
