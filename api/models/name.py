from dataclasses import dataclass

@dataclass
class Name:
    """
    A simple helper class for Names adding a comparator for better readability
    """

    length: int
    name: str
    keywords: list[str]
    keyword_scores: list[int]
    name_length_score: int
    name_score: int
    available: bool = False

    def __eq__(self, o: object) -> bool:
        return self.name == o.name

    def __ne__(self, o: object) -> bool:
        return self.name != o.name

    def __hash__(self) -> int:
        return hash(
            (
                self.length,
                self.name,
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
