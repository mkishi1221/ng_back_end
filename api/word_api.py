#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
import orjson as json
from typing import List
from .models.keyword import Keyword

small_wordsAPI_dict_filepath = "dict/wordsAPI_compact.json"
wordsAPI_data = json.loads(open(small_wordsAPI_dict_filepath, "rb").read())
wordsAPI_data_keys = wordsAPI_data.keys()


async def fetch_pos_wordAPI(word: str):

    # Get all "parts of speech" (pos) associated with each keyword.
    # If keyword is not in wordsAPI dictionary, return pos as empty string.
    pos_list = set()

    # Check if keyword is in wordsAPI dictionary.
    if word in wordsAPI_data_keys:
        if "definitions" in wordsAPI_data[word].keys():
            def_list = wordsAPI_data[word]["definitions"]

            # Loop through all the definitions tied to the same keyword.
            # Check if pos data is available, is a string and is not already in pos list.
            # If all above is true, add to pos list. Otherwise return pos as empty string.
            pos_list = {
                def_data["partOfSpeech"]
                for def_data in def_list
                if (
                    "partOfSpeech" in def_data.keys()
                    and isinstance(def_data["partOfSpeech"], str)
                )
            }

    return pos_list


async def update_pos_value(keyword: Keyword) -> List[Keyword]:

    # Get all possible pos using the fetch_pos_wordAPI function and add different pos variations to keyword list.
    # Do for both keyword and lemma word and collect all possible pos.
    updated_keywords_db = []
    pos_list = {
        pos
        for pos_list in await asyncio.gather(
            *[
                fetch_pos_wordAPI(keyword.keyword),
                fetch_pos_wordAPI(keyword.lemma),
            ]
        )
        for pos in pos_list
    }

    # Add different pos variations to keyword list.
    for pos in pos_list:
        keyword.wordsAPI_pos = pos
        updated_keywords_db.append(keyword)

    return updated_keywords_db


async def verify_word_with_wordsAPI(keyword: Keyword) -> List[Keyword]:
    return await update_pos_value(keyword)
