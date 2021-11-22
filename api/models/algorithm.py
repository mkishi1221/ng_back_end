from pydantic.dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Algorithm:
    """
    Helper class for manipulation of keywords
    """

    keyword_type_1: str
    keyword_type_2: str
    joint: str

    def __init__(self, keyword_type_1, keyword_type_2, joint):
        self.keyword_type_1 = keyword_type_1
        self.keyword_type_2 = keyword_type_2
        self.joint = joint if type(joint) != float else ""

    def __eq__(self, o: object) -> bool:
        return (
            self.keyword_type_1 == o.keyword_type_1
            and self.keyword_type_2 == o.keyword_type_2
            and self.joint == o.joint
        )

    def __ne__(self, o: object) -> bool:
        return (
            self.keyword_type_1 != o.keyword_type_1
            and self.keyword_type_2 != o.keyword_type_2
            and self.joint != o.joint
        )

    def __hash__(self) -> int:
        return hash((self.keyword_type_1, self.keyword_type_2, self.joint))

    def __repr__(self) -> str:
        return f"{self.keyword_type_1} + {f'{self.joint} + ' if self.joint else ''}{self.keyword_type_2}"
