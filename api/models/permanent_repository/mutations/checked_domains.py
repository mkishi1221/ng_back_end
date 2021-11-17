from typing import Dict, List
from models.domain import Domain
from ..repository import PermanentRepository


class CheckedDomainsMutations(PermanentRepository):
    @staticmethod
    def get_domains() -> List[Domain]:
        def construct_domain(d: Dict):
            del d["_id"]
            return Domain(**d)

        return [construct_domain(domain) for domain in PermanentRepository.checked_domains.find()]

    @staticmethod
    def upsert_domain(domain: Domain):
        """
        Upsert a single domain into cache (updating its' occurrence if allready exists)
        """
        domains = CheckedDomainsMutations.get_domains()
        if domain in domains:
            old_indx = domains.index(domain)
            domain.occurrence += domains[old_indx].occurrence
            return PermanentRepository.checked_domains.update_one(
                {"name": domain.name}, {"$set": domain}
            )
        else:
            return PermanentRepository.checked_domains.update_one(
                {"name": domain.name}, {"$set": domain.__dict__}, upsert=True
            )

    @staticmethod
    def remove_domain(domain: Domain):
        return PermanentRepository.checked_domains.delete_one(
            {"name": domain.name, "date_checked": domain.date_checked}
        )
