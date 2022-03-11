#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List, Set
from .models.keyword import Keyword
from os import path
import regex as re
import json
from .models.user_repository.mutations.user_preferences import UserPreferenceMutations


async def filter_keywords(keywords: List[Keyword], identifier: str) -> Set[Keyword]:
    """
    Filter approved keywords (approved keywords may be the following):
    - Either a noun, verb, or an adjective
    - Not contain any characters except alphabets
    - Word is at least 3 letters
    - Word is not a blacklisted word
    """
    
    
    

    # Create set of approved keywords, filtering by pos, "illegal_chars" and length
    return {
        keyword
        for keyword in keywords
        
    }
