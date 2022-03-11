#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from time import perf_counter
from typing import List
from .get_keyword_wiki_scores import get_keyword_wiki_scores

from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)
from .word_api import verify_word_with_wordsAPI
from .models.keyword import Keyword
import regex as re
import spacy
from joblib import Parallel, delayed
from loky import set_loky_pickler

nlp = spacy.load(
    "en_core_web_lg",
    exclude=[
        "ner",
        "entity_linker",
        "entity_ruler",
        "textcat",
        "textcat_multilabel",
        "morphologizer",
        "senter",
        "sentencizer",
        "tok2vec",
        "transformer",
    ],
)

approved_pos = ["noun", "verb", "adjective"]
illegal_char = re.compile(r"[^a-zA-Z]")
illegal_start_end = re.compile(r"^\W+|\W+$")


async def create_keyword(word, word_pos, word_lemma, blacklisted_words) -> Keyword:
    """
    summary:
        Creates a "keyword" so that similar words are grouped together regardless of their case-styles/symbols used.
        Removes non-alphabet characters from beginning and end of word and saves it as lowercase "keyword".
        (eg. "+High-tech!" → "high-tech" )
    parameters:
        word: str; word to create keyword from
        word_pos: str; Coarse-grained part-of-speech from the Universal POS tag set. (eg. noun, verb etc.)
        word_lemma: str; Base form of the token, with no inflectional suffixes. (eg. word = changing, lemma = change)
    returns:
        token_dict: dict; a dictionary containing all important parameters of keyword
    """

    if word in blacklisted_words or bool(illegal_char.search(keyword.keyword)) or word_pos not in approved_pos:
        return

    keyword = illegal_start_end.sub("", word)
    res = Keyword(
        word=word,
        keyword_len=len(keyword),
        keyword=keyword.lower(),
        origin="spacy",
        spacy_pos=word_pos,
        lemma=word_lemma,
    )
    return get_keyword_wiki_scores(await verify_word_with_wordsAPI(res))


async def generate_keywords(lines: str, identifier: str) -> List[Keyword]:

    keyword_blacklist = await UserPreferenceMutations.get_blacklisted(identifier)

    docs = nlp.pipe(lines.split(". "), n_process=4, batch_size=25)

    # set_loky_pickler("pickle")

    start = perf_counter()
    # Spacy divides sentences ("sent") into words ("tokens").
    # Tokens can also be symbols and other things that are not full words.
    keywords: List[Keyword] = Parallel(n_jobs=2)(
        delayed(create_keyword)(token.text, token.pos_, token.lemma_, keyword_blacklist)
        for doc in docs
        for sent in doc.sents
        for token in sent
    )

    print(f"{perf_counter() - start: 0.4f} for keyword gen")

    def count_occurence(k: Keyword):
        k.occurrence = keywords.count(k)
        return k

    unique_words = {
        count_occurence(k)
        for k in filter(
            lambda k: k.keyword_len >= 2 and not re.match("\d", k.word), keywords
        )
    }

    # Sort keyword list according to:
    # - "keyword" in alphabetical order
    # - occurrence
    # - "original" word in alphabetical order.
    sorted_unique_words = sorted(
        unique_words, key=lambda k: (k.keyword, -k.occurrence, k.word.lower())
    )

    return sorted_unique_words
