from typing import Dict, List
from fastapi import FastAPI, WebSocket
from fastapi.security import HTTPBearer
import orjson as json
from api.filter_keywords import filter_keywords
from fastapi.middleware.cors import CORSMiddleware

from api.models.keyword import Keyword
from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)
from api.models.user_repository.repository import UserRepository
from api.routes import algorithm_collector, blacklist_collector, whitelist_collector
from .event_handler import emitter, ConnectionManager
import asyncio
from .models.permanent_repository.repository import PermanentRepository
from .models.algorithm import Algorithm
from .combine_words import combine_words

from .routes import words_collector

UserRepository.init_user()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

token_auth_scheme = HTTPBearer()
app = FastAPI()
app.include_router(words_collector.router)
app.include_router(algorithm_collector.router)
app.include_router(blacklist_collector.router)
app.include_router(whitelist_collector.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
manager = ConnectionManager()


@emitter.on("new_words")
def send_names(identifier: str):
    verbs = []
    nouns = []
    adjectives = []
    keywords = UserPreferenceMutations.get_greylisted()
    for word in keywords:
        if word.wordsAPI_pos == "verb":
            verbs.append(word)
        elif word.wordsAPI_pos == "noun":
            nouns.append(word)
        elif word.wordsAPI_pos == "adjective":
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

    algorithms = UserPreferenceMutations.get_algorithms()

    all_names = [
        name
        for alg in algorithms
        for name in combine_words(
            filter_keywords(keyword_dict[alg.keyword_type_1]),
            alg.keyword_type_1,
            filter_keywords(keyword_dict[alg.keyword_type_2]),
            alg.keyword_type_2,
            alg,
        )
    ]

    all_names = sorted(all_names, key=lambda k: (k.name_score * -1, k.name))

    loop = asyncio.get_event_loop()
    loop.create_task(
        manager.send(
            json.dumps(all_names, option=json.OPT_SERIALIZE_DATACLASS).decode("utf-8"),
            identifier,
        )
    )


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
