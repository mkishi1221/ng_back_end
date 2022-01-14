from typing import Dict, List
from fastapi import FastAPI, WebSocket
from fastapi.security import HTTPBearer
import orjson as json
from api.filter_keywords import filter_keywords
from fastapi.middleware.cors import CORSMiddleware
import functools

from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)
from api.routes import (
    algorithm_collector,
    blacklist_collector,
    settings,
    whitelist_collector,
)
from .event_handler import emitter, ConnectionManager
import asyncio
from .models.permanent_repository.repository import PermanentRepository
from .combine_words import combine_words

from .routes import words_collector

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://identitytobrand.com:3000",
]

token_auth_scheme = HTTPBearer()
app = FastAPI()
app.include_router(words_collector.router)
app.include_router(algorithm_collector.router)
app.include_router(blacklist_collector.router)
app.include_router(whitelist_collector.router)
app.include_router(settings.router)
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
    keywords = UserPreferenceMutations.get_whitelisted(identifier)
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
        "verb": filter_keywords(verbs, identifier),
        "noun": filter_keywords(nouns, identifier),
        "adjective": filter_keywords(adjectives, identifier),
        "prefix": prefixes,
        "suffix": suffixes,
    }

    algorithms = UserPreferenceMutations.get_algorithms(identifier)

    all_names = [
        name
        for alg in algorithms
        for name in combine_words(keyword_dict, alg)
    ]

    all_names = sorted(all_names, key=lambda k: (k.name_score * -1, k.name))

    loop = asyncio.get_event_loop()
    loop.create_task(
        manager.send(
            json.dumps(all_names, option=json.OPT_SERIALIZE_DATACLASS).decode("utf-8"),
            "names",
            identifier,
        )
    )


@app.websocket("/ws")
async def name_distributor(websocket: WebSocket, name: str, project: str):
    await manager.connect(websocket, name, project)
    UserPreferenceMutations.set_last_project(name, project)
    try:
        while 1:
            await websocket.send_json(
                {"type": "keepalive"}
            )  # keep the websocket connection alive
            await asyncio.sleep(30)
    except:
        manager.disconnect(websocket)
