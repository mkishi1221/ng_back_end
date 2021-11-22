from typing import Tuple

from api.models.keyword import Keyword
from .algorithm import Algorithm
from dataclasses import dataclass

@dataclass
class Name:
    """
    A simple helper class for Names adding a comparator for better readability
    """

    algorithm: Algorithm
    length: int
    name: str
    domain: str
    all_keywords: str
    keyword1: Tuple[str]
    keyword2: Tuple[str]
    keyword_1_score: int
    keyword_2_score: int
    name_length_score: int
    name_score: int

    def __eq__(self, o: object) -> bool:
        return self.name == o.name and self.all_keywords == o.all_keywords

    def __ne__(self, o: object) -> bool:
        return self.name != o.name and self.all_keywords != o.all_keywords

    def __hash__(self) -> int:
        return hash(
            (
                self.algorithm,
                self.length,
                self.name,
                self.domain,
                self.all_keywords,
                self.keyword1,
                self.keyword2,
                self.keyword_1_score,
                self.keyword_2_score,
                self.name_length_score,
                self.name_score,
            )
        )

    def __repr__(self) -> str:
        return str(
            {
                key: self.__dict__[key]
                for key in self.__dict__
                if self.__dict__[key] is not None
            }
        )
