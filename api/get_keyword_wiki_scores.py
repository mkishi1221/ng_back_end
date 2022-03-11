import orjson as json
from .models.keyword import Keyword
from typing import List


wiki_score_dict_filepath = "dict/wikipedia_word_count/wikipedia-en-words-cumulative.json"
score_data = json.loads(open(wiki_score_dict_filepath, "rb").read())
score_data_keys = score_data.keys()


def get_keyword_wiki_scores(keywords_db: List[Keyword]) -> List[Keyword]:

    updated_keywords_db = []
    for keyword_data in keywords_db:
        if keyword_data.keyword in score_data_keys:
            keyword_wiki_score = score_data[keyword_data.keyword]['keyword_score']
            keyword_data.keyword_wiki_score = keyword_wiki_score
            keyword_data.keyword_total_score = keyword_wiki_score + keyword_data.keyword_user_score
        updated_keywords_db.append(keyword_data)

    return updated_keywords_db
