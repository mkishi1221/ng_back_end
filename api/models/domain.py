from dataclasses import dataclass
from datetime import datetime
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Domain:
    name: str = ""
    availability: str = ""
    domain_expiration: int = -1
    date_checked: int = int(datetime.now().timestamp())
    occurrence: int = 0

    def __eq__(self, o: object) -> bool:
        return (
            self.name == o.name
            and self.availability == o.availability
            and self.domain_expiration == o.domain_expiration
        )

    def __ne__(self, o: object) -> bool:
        return (
            self.name != o.name
            and self.availability != o.availability
            and self.domain_expiration != o.domain_expiration
        )

    def __hash__(self) -> int:
        return hash((self.name, self.availability, self.domain_expiration))
