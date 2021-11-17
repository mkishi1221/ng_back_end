from typing import Dict, List
from fastapi import FastAPI, WebSocket
from fastapi.security import HTTPBearer
import orjson as json

from api.models.keyword import Keyword
from .event_handler import emitter, ConnectionManager
import asyncio
from .models.permanent_repository.repository import PermanentRepository
from .models.algorithm import Algorithm
from .combine_words import combine_words

from .routes import words_collector

token_auth_scheme = HTTPBearer()
app = FastAPI()
app.include_router(words_collector.router)
manager = ConnectionManager()


@emitter.on("new_words")
def send_names(keywords: List[Keyword], identifier: str):
    verbs = []
    nouns = []
    adjectives = []
    for word in keywords:
        if word["wordsAPI_pos"] == "verb":
            verbs.append(word)
        elif word["wordsAPI_pos"] == "noun":
            nouns.append(word)
        elif word["wordsAPI_pos"] == "adjective":
            adjectives.append(word)

    prefixes = [prefix_obj for prefix_obj in PermanentRepository.prefixes.find()]
    suffixes = [suffix_obj for suffix_obj in PermanentRepository.suffixes.find()]

    keyword_dict = {
        "verb": verbs,
        "noun": nouns,
        "adjective": adjectives,
        "prefix": prefixes,
        "suffix": suffixes,
    }

    def combine(alg: Algorithm):
        print(
            f"Generating names with {alg}..."
        )

        return combine_words(
            keyword_dict[alg.keyword_type_1],
            alg.keyword_type_1,
            keyword_dict[alg.keyword_type_2],
            alg.keyword_type_2,
            alg,
        )

    all_names = [name for alg in algorithms for name in combine(alg)]
    all_names = sorted(all_names, key=lambda k: (k.name_score * -1, k.name))
    
    loop = asyncio.get_event_loop()
    loop.create_task(manager.send(json.dumps(all_names, option=json.OPT_SERIALIZE_DATACLASS), identifier))


@app.websocket("/ws")
async def name_distributor(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while 1:
            await websocket.send_text(
                "keepalive"
            )  # keep the websocket connection alive
            await asyncio.sleep(30)
    except:
        manager.disconnect(websocket)
