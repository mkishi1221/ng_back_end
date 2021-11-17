#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import json
import os
from typing import List
from .models.keyword import Keyword
import regex as re


def create_small_wordAPI(keywords: List[Keyword], wordapi_data: dict):

    # Create smaller portable version of wordAPI dictionary containing words in the source data.
    # Add "keyword" to word list. Dictionary will comprise of words in this word list.
    # If lowercase "lemma" is different to lowercase "keyword", add to word list as well
    
    word_list = []
    for keyword in keywords:
        word_base = str(keyword.keyword)
        word_list.append(word_base)

        word_lemma = str(keyword.lemma)
        if word_lemma != "" and word_lemma.lower() != word_base:
            word_list.append(word_lemma)

    # Get all dictionary data listed for each word
    small_wordsAPI = {
        word: wordapi_data[word] for word in word_list if word in wordapi_data.keys()
    }

    return small_wordsAPI


def fetch_pos_wordAPI(word: str, wordapi_data: dict):

    # Get all "parts of speech" (pos) associated with each keyword.
    # If keyword is not in wordsAPI dictionary, return pos as empty string.
    pos_list = []

    # Check if keyword is a number (Integer and float). If number, pos is NUM.
    if re.match("^[0-9.]*$", word or "") is not None:
        pos_list.append("NUM")

    # Check if keyword is in wordsAPI dictionary.
    elif word in wordapi_data.keys():
        if "definitions" in wordapi_data[word].keys():
            def_list = wordapi_data[word]["definitions"]

            # Loop through all the definitions tied to the same keyword.
            # Check if pos data is available, is a string and is not already in pos list.
            # If all above is true, add to pos list. Otherwise return pos as empty string.
            pos_list = [
                def_data["partOfSpeech"]
                for def_data in def_list
                if (
                    "partOfSpeech" in def_data.keys()
                    and isinstance(def_data["partOfSpeech"], str)
                    and def_data["partOfSpeech"] not in pos_list
                )
            ]

    return pos_list


def update_pos_value(
    keywords_db: List[Keyword], wordsAPI_data: dict
) -> List[Keyword]:

    # Get all possible pos using the fetch_pos_wordAPI function and add different pos variations to keyword list.
    # Do for both keyword and lemma word and collect all possible pos.
    updated_keywords_db = []
    for keyword_data in keywords_db:
        pos_list_keyword_n_lemma = set()

        keyword_b = keyword_data.keyword
        keyword_b_pos = fetch_pos_wordAPI(keyword_b, wordsAPI_data)
        pos_list_keyword_n_lemma.update(keyword_b_pos)

        keyword_l = keyword_data.lemma
        keyword_l_pos = fetch_pos_wordAPI(keyword_l, wordsAPI_data)
        pos_list_keyword_n_lemma.update(keyword_l_pos)

        # Remove duplicate pos
        pos_list = {pos for pos in pos_list_keyword_n_lemma}

        # Add different pos variations to keyword list.
        for pos in pos_list:
            keyword_data.wordsAPI_pos = pos
            updated_keywords_db.append(keyword_data)

    return updated_keywords_db


def verify_words_with_wordsAPI(keywords_db: List[Keyword]) -> List[Keyword]:

    main_wordsAPI_dict_filepath = "../wordsAPI/original_data/wordsapi_list.json"
    small_wordsAPI_dict_filepath = "dict/wordsAPI_compact.json"

    # Check if full wordsAPI dictionary is available.
    # If full wordsAPI dictionary is available, create a smaller version.
    try:
        with open(main_wordsAPI_dict_filepath) as wordsAPI_file:
            wordsAPI_data = json.load(wordsAPI_file)

        small_wordsAPI = create_small_wordAPI(keywords_db, wordsAPI_data)
        with open(small_wordsAPI_dict_filepath, "w+") as out_file:
            json.dump(small_wordsAPI, out_file, ensure_ascii=False, indent=1)

        # Take in keyword list created by spacy and add wordAPI pos data as well as other pos variations.
        updated_keywords_db = update_pos_value(keywords_db, wordsAPI_data)

    # If full wordsAPI dictionary is not available, use smaller version.
    except FileNotFoundError:
        with open(small_wordsAPI_dict_filepath) as wordapi_file:
            wordsAPI_data = json.load(wordapi_file)

        # Take in keyword list and add wordAPI pos data as well as other pos variations.
        updated_keywords_db = update_pos_value(keywords_db, wordsAPI_data)

    return updated_keywords_db
