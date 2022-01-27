from pydantic.dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional
import uuid


@dataclass_json
@dataclass
class Keyword:
    """
    A simple helper class for keywords adding a comparator for better readability
    """

    id: int = 0
    word: Optional[str] = None
    keyword_len: int = 0
    keyword: str = ""
    origin: Optional[str] = None
    spacy_pos: Optional[str] = None
    wordsAPI_pos: str = ""
    lemma: Optional[str] = None
    algorithm: Optional[str] = None
    occurrence: int = 0
    keyword_user_score: int = 0
    keyword_wiki_score: int = 0
    keyword_total_score: int = 0

    def __init__(
        self,
        id: Optional[int] = 0,
        word: Optional[str] = "",
        keyword_len: Optional[int] = 0,
        keyword: Optional[str] = "",
        origin: Optional[str] = "",
        spacy_pos: Optional[str] = "",
        wordsAPI_pos: Optional[str] = "",
        lemma: Optional[str] = "",
        algorithm: Optional[str] = "",
        occurrence: Optional[int] = 0,
        keyword_user_score: Optional[int] = 0,
        keyword_wiki_score: Optional[int] = 0,
        keyword_total_score: Optional[int] = 0,
    ):
        self.word = word
        self.keyword_len = keyword_len
        self.keyword = keyword
        self.origin = origin
        self.spacy_pos = spacy_pos
        self.wordsAPI_pos = wordsAPI_pos
        self.lemma = lemma
        self.algorithm = algorithm
        self.occurrence = occurrence
        self.keyword_user_score = keyword_user_score
        self.keyword_wiki_score = keyword_wiki_score
        self.keyword_total_score = keyword_total_score
        self.id = hash((self.word, self.keyword_len, self.keyword, self.origin))

    def __eq__(self, o: object) -> bool:
        return self.keyword == o.keyword and self.wordsAPI_pos == o.wordsAPI_pos

    def __ne__(self, o: object) -> bool:
        return self.keyword != o.keyword and self.wordsAPI_pos != o.wordsAPI_pos

    def __hash__(self) -> int:
        return hash((self.word, self.keyword_len, self.keyword, self.origin))

    def __repr__(self) -> str:
        return str(
            {
                key: self.__dict__[key]
                for key in self.__dict__
                if self.__dict__[key] is not None
            }
        )
