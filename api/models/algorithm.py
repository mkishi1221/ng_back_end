from typing import List
from pydantic.dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Algorithm:
    """
    Helper class for manipulation of keywords
    """

    id: int
    components: List[str]

    def __init__(self, id: int, components: List[str]):
        self.components = components
        self.id = hash("".join(components))

    def __eq__(self, o: object) -> bool:
        return self.id == o.id

    def __ne__(self, o: object) -> bool:
        return self.id != o.id

    def __hash__(self) -> int:
        return hash("".join(self.components))

    def __repr__(self) -> str:
        return " + ".join(self.components)
