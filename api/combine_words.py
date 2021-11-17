#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from .models.algorithm import Algorithm
from .models.name import Name


def combine_words(wordlist1: List[dict], wordlist_1_type: str, wordlist2: List[dict], wordlist_2_type: str, algorithm: Algorithm) -> List[Name]:

    # Combine keywords from 2 keyword lists
    joint = algorithm.joint
    name_list: list[Name] = []
    for keyword_1_dict in wordlist1:
        if wordlist_1_type == 'prefix':
            keyword_1 = keyword_1_dict['prefix']
            keyword_1_user_score = 'user: 2'
            keyword_1_wiki_score = 'wiki: 0'
            keyword_1_score = 2
            keyword_1_origin = 'dictionary'
        else:
            keyword_1 = keyword_1_dict['keyword'].title()
            keyword_1_user_score = 'user: ' + str(keyword_1_dict['keyword_user_score'])
            keyword_1_wiki_score = 'wiki: ' + str(keyword_1_dict['keyword_wiki_score'])
            keyword_1_score = keyword_1_dict['keyword_total_score']
            keyword_1_origin = keyword_1_dict['origin']

        for keyword_2_dict in wordlist2:
            if wordlist_2_type == 'suffix':
                keyword_2 = keyword_2_dict['suffix']
                keyword_2_user_score = 'user: 2'
                keyword_2_wiki_score = 'wiki: 0'
                keyword_2_score = 2
                keyword_2_origin = 'dictionary'
            else:
                keyword_2 = keyword_2_dict['keyword'].title()
                keyword_2_user_score = 'user: ' + str(keyword_2_dict['keyword_user_score'])
                keyword_2_wiki_score = 'wiki: ' + str(keyword_2_dict['keyword_wiki_score'])
                keyword_2_score = keyword_2_dict['keyword_total_score']
                keyword_2_origin = keyword_2_dict['origin']

            name = joint.join((keyword_1, keyword_2))
            domain = name.lower() + ".com"
            all_keywords = "| " + keyword_1 + " | " + keyword_2 + " |"

            # Additional score based on length of name
            name_length_score = 0
            name_length = len(name)
            if name_length <= 6:
                name_length_score = 3
            elif name_length <= 8:
                name_length_score = 2
            elif name_length <= 10:
                name_length_score = 1
            else:
                name_length_score = 0

            name_score = int(keyword_1_score) + int(keyword_2_score) + int(name_length_score)
            name_list.append(
                Name(
                    repr(algorithm),
                    len(name),
                    name,
                    domain,
                    all_keywords,
                    (keyword_1, wordlist_1_type, keyword_1_user_score, keyword_1_wiki_score, keyword_1_origin),
                    (keyword_2, wordlist_2_type, keyword_2_user_score, keyword_2_wiki_score, keyword_2_origin),
                    keyword_1_score,
                    keyword_2_score,
                    name_length_score,
                    name_score
                )
            )

    # Filter out names that are more than 15 characters
    temp_set = {
        combined_word for combined_word in name_list if combined_word.length <= 15
    }

    # Sort name list by alphabetical order and length.
    name_list = list(temp_set)
    name_list.sort(
        key=lambda combined_name: getattr(combined_name, "name").lower(), reverse=False
    )
    sorted_by_len_name_list = sorted(
        name_list,
        key=lambda combined_name: getattr(combined_name, "length"),
        reverse=False,
    )

    return sorted_by_len_name_list
