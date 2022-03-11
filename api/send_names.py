import orjson as json
import aiohttp
import copy
import asyncio

from api.filter_keywords import filter_keywords
from api.models.user_repository.mutations.user_preferences import UserPreferenceMutations
from .main import manager
from .models.permanent_repository.repository import PermanentRepository
from .combine_words import combine_words
from .event_handler import emitter


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
            if "domains" not in jsonResp:
                return
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
    loop = asyncio.get_event_loop()
    loop.create_task(send_names_async(identifier))


async def send_names_async(identifier: str):
    verbs = []
    nouns = []
    adjectives = []
    keywords = await UserPreferenceMutations.get_whitelisted(identifier)
    for word in keywords:
        if word.wordsAPI_pos == "verb":
            verbs.append(word)
        elif word.wordsAPI_pos == "noun":
            nouns.append(word)
        elif word.wordsAPI_pos == "adjective":
            adjectives.append(word)

    prefixes = [prefix_obj for prefix_obj in PermanentRepository.prefixes.find()]
    suffixes = [suffix_obj for suffix_obj in PermanentRepository.suffixes.find()]
    tlds = [tld for tld in await UserPreferenceMutations.get_tlds(identifier)]

    keyword_dict = {
        "verb": filter_keywords(verbs, identifier),
        "noun": filter_keywords(nouns, identifier),
        "adjective": filter_keywords(adjectives, identifier),
        "prefix": prefixes,
        "suffix": suffixes,
    }

    algorithms = await UserPreferenceMutations.get_algorithms(identifier)

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