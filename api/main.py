from fastapi import FastAPI, WebSocket
from fastapi.security import HTTPBearer
import orjson as json
from api.filter_keywords import filter_keywords
from fastapi.middleware.cors import CORSMiddleware

from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)
from api.routes import (
    algorithm_collector,
    blacklist_collector,
    settings,
    whitelist_collector,
    words_collector,
    tld_collector,
)
from .event_handler import emitter, ConnectionManager
import asyncio
from .models.permanent_repository.repository import PermanentRepository
from .combine_words import combine_words
import aiohttp
import copy


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://identitytobrand.com:3000",
]

token_auth_scheme = HTTPBearer()
app = FastAPI(title="identitytobrand lofi api", version="0.0.1")
app.include_router(words_collector.router)
app.include_router(algorithm_collector.router)
app.include_router(blacklist_collector.router)
app.include_router(whitelist_collector.router)
app.include_router(tld_collector.router)
app.include_router(settings.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
manager = ConnectionManager()


def merge_availabilities(domain, availability):
    domain.available = availability
    return domain


async def create_domains(domains, identifier):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.godaddy.com/v1/domains/available?checkType=FULL",
            json=list(map(lambda d: d.name, domains)),
            headers={
                "authorization": "sso-key dLDKcLmoPp7m_6NPFNwrzL37ZuUqeK1QZ8S:UAhhomshJZaoVedg6VMqmS"
            },
        ) as resp:
            jsonResp = await resp.json()
            availabilities = [a["available"] for a in jsonResp["domains"]]

            domains = [
                merge_availabilities(domain, availabilities[i])
                for i, domain in enumerate(domains)
            ]

            await manager.send(
                json.dumps(domains, option=json.OPT_SERIALIZE_DATACLASS).decode(
                    "utf-8"
                ),
                "names",
                identifier,
            )


@emitter.on("generate_names")
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
    tlds = [tld for tld in UserPreferenceMutations.get_tlds(identifier)]

    keyword_dict = {
        "verb": filter_keywords(verbs, identifier),
        "noun": filter_keywords(nouns, identifier),
        "adjective": filter_keywords(adjectives, identifier),
        "prefix": prefixes,
        "suffix": suffixes,
    }

    algorithms = UserPreferenceMutations.get_algorithms(identifier)

    all_names = [
        name for alg in algorithms for name in combine_words(keyword_dict, alg)
    ]

    all_names = sorted(all_names, key=lambda k: (k.name_score * -1, k.name))

    def domainify(name, tld):
        n = copy.copy(name)
        n.name = f"{name.name}{tld}"
        return n

    domains = [domainify(name, tld) for name in all_names for tld in tlds]

    loop = asyncio.get_event_loop()
    loop.create_task(create_domains(domains, identifier))


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
