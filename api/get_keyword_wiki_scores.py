import orjson as json
from .models.keyword import Keyword
from typing import List

def get_keyword_wiki_scores(keywords_db: List[Keyword]) -> List[Keyword]:

    with open("dict/wikipedia_word_count/wikipedia-en-words-cumulative.json", "rb") as keyword_wiki_score_data_file:
        keyword_wiki_score_data = json.loads(keyword_wiki_score_data_file.read())

    updated_keywords_db = []
    for keyword_data in keywords_db:
        if keyword_data.keyword in keyword_wiki_score_data.keys():
            keyword_wiki_score = keyword_wiki_score_data[keyword_data.keyword]['keyword_score']
            keyword_data.keyword_wiki_score = keyword_wiki_score
            keyword_data.keyword_total_score = keyword_wiki_score + keyword_data.keyword_user_score
        updated_keywords_db.append(keyword_data)

    return updated_keywords_db
