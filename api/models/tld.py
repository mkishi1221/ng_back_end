from pydantic.dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class TLD:
    """
    A simple helper class for TLDs
    """

    inUse: bool
    tld: str

    def __eq__(self, o: object) -> bool:
        return self.tld == o.tld

    def __ne__(self, o: object) -> bool:
        return self.tld != o.tld

    def __hash__(self) -> int:
        return hash(
            (
+                self.tld
            )
        )

    def __repr__(self) -> str:
        return f"{self.tld}"
