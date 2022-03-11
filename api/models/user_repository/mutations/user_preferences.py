from api.event_handler import ConnectionManager
from api.models.algorithm import Algorithm
from api.models.tld import TLD
from ...name import Name
from ...keyword import Keyword
from typing import List, Dict, Union
from ...user_repository.repository import UserRepository
from fastapi import status, Response
import orjson as json


class UserPreferenceMutations(UserRepository):
    @staticmethod
    def user_specific_preference_list(identifier: str) -> Union[Dict, None]:
        return UserRepository.list_collection.find_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id}
        )

    # region upserts
    @staticmethod
    async def _upsert_keyword_in_list(
        list_entry: Union[Keyword, Name], list_id: str, identifier: str
    ):
        """
        General method to upsert (update or insert if not existent) a keyword in the lists document
        """
        user_list = UserPreferenceMutations.user_specific_preference_list(identifier)
        if isinstance(list_entry, Keyword):
            try:
                to_update = next(
                    (
                        entry
                        for entry in user_list[list_id]
                        if Keyword.from_dict(entry) == list_entry
                    ),
                    None,
                )  # filter for correct keyword
            except KeyError:
                to_update = None
        elif isinstance(list_entry, Name):
            to_update = next(
                (
                    entry
                    for entry in user_list[list_id]
                    if entry["name"] == list_entry.name
                ),
                None,
            )  # filter for correct keyword

        if not to_update:
            setattr(list_entry, "occurrence", 1)
            to_upsert = list_entry.__dict__
            try:
                to_upsert.pop("__initialised__")
            except:
                pass  # pydantic didn't add __initialised__
            return UserRepository.list_collection.update_one(
                {"project_id": ConnectionManager.get_user(identifier).project_id},
                {"$addToSet": {list_id: to_upsert}},
            )

        else:
            to_update["occurrence"] += 1

            return UserRepository.list_collection.update_one(
                {
                    "project_id": ConnectionManager.get_user(identifier).project_id,
                    f"{list_id}.{'keyword' if isinstance(list_entry, Keyword) else 'name'}": list_entry.keyword
                    if isinstance(list_entry, Keyword)
                    else list_entry.name,
                },
                {"$set": {f"{list_id}.$.occurrence": to_update["occurrence"]}},
            )

    @staticmethod
    async def set_last_project(user: str, project_name: str):
        UserRepository.profile_collection.update_one(
            {"user": user}, {"$set": {"last_project": project_name}}
        )

    ## algorithms
    @staticmethod
    async def upsert_algorithm(algorithm: Algorithm, identifier: str):
        """
        Method to upsert keyword in algorithm list of user
        """
        known_algorithms = UserPreferenceMutations.get_algorithms(identifier)
        if algorithm in known_algorithms:
            return Response(status_code=status.HTTP_409_CONFLICT)
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id},
            {"$addToSet": {"algorithms": algorithm.__dict__}},
        )
        known_algorithms.append(algorithm)
        return known_algorithms

    @staticmethod
    async def upsert_tld(tld: TLD, identifier: str):
        """
        Method to upsert tld in tld list of user
        """
        known_tlds = UserPreferenceMutations.get_tlds(identifier)
        if tld in known_tlds:
            return Response(status_code=status.HTTP_409_CONFLICT)
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id},
            {"$addToSet": {"tlds": tld.__dict__}},
        )
        known_tlds.append(tld)
        return known_tlds

    ## blacklist
    @staticmethod
    async def upsert_keyword_in_blacklist(keyword: Keyword, identifier: str):
        """
        Method to upsert keyword in blacklist of user; uses _upsert_keyword_in_list
        """
        return await UserPreferenceMutations._upsert_keyword_in_list(keyword, "black", identifier)

    @staticmethod
    async def upsert_multiple_keywords_in_blacklist(keywords: List[Keyword], identifier: str):
        """
        Method to upsert multiple keywords in blacklist of user; uses _upsert_keyword_in_list
        """
        res = None
        for keyword in keywords:
            res = await UserPreferenceMutations._upsert_keyword_in_list(keyword, "black", identifier)
        return res

    ## greylist
    @staticmethod
    async def upsert_keyword_in_greylist(keyword: Keyword, identifier: str):
        """
        Method to upsert keyword in greylist of user; uses _upsert_keyword_in_list
        """
        return await UserPreferenceMutations._upsert_keyword_in_list(keyword, "grey", identifier)

    @staticmethod
    async def upsert_multiple_keywords_in_greylist(keywords: List[Keyword], identifier: str):
        """
        Method to upsert multiple keywords in greylist of user; uses _upsert_keyword_in_list
        """
        res = None
        for keyword in keywords:
            res = await UserPreferenceMutations._upsert_keyword_in_list(keyword, "grey", identifier)
        return res

    ## whitelist
    @staticmethod
    async def upsert_keyword_in_whitelist(keyword: Keyword, identifier: str):
        """
        Method to upsert keyword in whitelist of user; uses _upsert_keyword_in_list
        """
        return await UserPreferenceMutations._upsert_keyword_in_list(keyword, "white", identifier)

    @staticmethod
    async def upsert_multiple_keywords_in_whitelist(keywords: List[Keyword], identifier: str):
        """
        Method to upsert multiple keywords in whitelist of user; uses _upsert_keyword_in_list
        """
        res = None
        for keyword in keywords:
            res = await UserPreferenceMutations._upsert_keyword_in_list(keyword, "white", identifier)
        return res

    ## shortlist
    @staticmethod
    async def upsert_keyword_in_shortlist(keyword: Name, identifier: str):
        """
        Method to upsert keyword in shortlist of user; uses _upsert_keyword_in_list
        """
        return await UserPreferenceMutations._upsert_keyword_in_list(keyword, "short", identifier)

    @staticmethod
    async def upsert_multiple_keywords_in_shortlist(keywords: List[Name], identifier: str):
        """
        Method to upsert multiple keywords in shortlist of user; uses _upsert_keyword_in_list
        """
        res = None
        for keyword in keywords:
            res = await UserPreferenceMutations._upsert_keyword_in_list(keyword, "short", identifier)
        return res

    # endregion

    # region getters
    ## algorithms
    @staticmethod
    async def get_algorithms(identifier: str) -> List[Algorithm]:
        """
        Returns all algorithms in preference list of user
        """
        return Algorithm.schema().loads(
            json.dumps(
                UserPreferenceMutations.user_specific_preference_list(identifier)["algorithms"]
            ),
            many="True",
        )

    ## tlds
    @staticmethod
    async def get_tlds(identifier: str) -> List[TLD]:
        """
        Returns all algorithms in preference list of user
        """
        return TLD.schema().loads(
            json.dumps(
                UserPreferenceMutations.user_specific_preference_list(identifier)["tlds"]
            ),
            many="True",
        )

    ## blacklist
    @staticmethod
    async def get_blacklisted(identifier: str) -> List[Keyword]:
        """
        Returns all keywords in the blacklist of current user
        """
        return Keyword.schema().loads(
            json.dumps(
                UserPreferenceMutations.user_specific_preference_list(identifier)["black"]
            ),
            many=True,
        )

    ## greylist
    @staticmethod
    async def get_greylisted(identifier: str) -> List[Keyword]:
        """
        Returns all keywords in the greylist of current user
        """
        return Keyword.schema().loads(
            json.dumps(UserPreferenceMutations.user_specific_preference_list(identifier)["grey"]),
            many=True,
        )

    ## whitelist
    @staticmethod
    async def get_whitelisted(identifier: str) -> List[Keyword]:
        """
        Returns all keywords in the whitelist of current user
        """
        return Keyword.schema().loads(
            json.dumps(
                UserPreferenceMutations.user_specific_preference_list(identifier)["white"]
            ),
            many=True,
        )

    ## shortlist
    @staticmethod
    async def get_shortlisted(identifier: str) -> List[Name]:
        """
        Returns all names in the shortlist of current user
        """

        def remove_occurence(word: Dict):
            del word["occurrence"]
            return Name(**word)

        return [
            remove_occurence(word)
            for word in UserPreferenceMutations.user_specific_preference_list(identifier)["short"]
        ]

    # settings
    @staticmethod
    async def get_profile(user: str):
        """
        Returns settings of user
        """

        res = UserRepository.profile_collection.find_one({"user": user})
        if res:
            res.pop("_id")
        return res

    # endregion

    # region removers
    ## blacklist
    @staticmethod
    async def remove_from_blacklist(word: str, identifier: str):
        removed = filter(lambda keyword: keyword["word"] == word, UserPreferenceMutations.user_specific_preference_list(identifier)["black"])
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id},
            {"$pull": {"black": {"word": word}}},
        )
        return next(removed)

    ## greylist
    @staticmethod
    async def remove_from_greylist(word: str, identifier: str):
        removed = filter(lambda keyword: keyword["word"] == word, UserPreferenceMutations.user_specific_preference_list(identifier)["grey"])
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id},
            {"$pull": {"grey": {"word": word}}},
        )
        return next(removed)

    ## whitelist
    @staticmethod
    async def remove_from_whitelist(word: str, identifier: str):
        removed = filter(lambda keyword: keyword["word"] == word, UserPreferenceMutations.user_specific_preference_list(identifier)["white"])
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id},
            {"$pull": {"white": {"word": word}}},
        )
        return next(removed)

    ## shortlist
    @staticmethod
    async def remove_from_shortlist(word: str, identifier: str):
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id},
            {"$pull": {"short": {"word": word}}},
        )

    ## algorithms
    @staticmethod
    async def remove_from_algorithms(algorithmID: str, identifier: str):
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id},
            {"$pull": {"algorithms": {"id": algorithmID}}},
        )

    ## tlds
    @staticmethod
    async def remove_from_tlds(tld: str, identifier: str):
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id},
            {"$pull": {"tlds": {"tld": tld}}},
        )

    # endregion

    # dev methods
    @staticmethod
    async def _drop_blacklist(identifier: str):
        """
        Only use this method in a developer environment AND WHEN YOU'RE COMPLETELY SURE WHAT YOU ARE DOING!
        """
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id}, {"$set": {"black": []}}
        )

    @staticmethod
    async def _drop_greylist(identifier: str):
        """
        Only use this method in a developer environment AND WHEN YOU'RE COMPLETELY SURE WHAT YOU ARE DOING!
        """
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id}, {"$set": {"grey": []}}
        )

    @staticmethod
    async def _drop_whitelist(identifier: str):
        """
        Only use this method in a developer environment AND WHEN YOU'RE COMPLETELY SURE WHAT YOU ARE DOING!
        """
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id}, {"$set": {"white": []}}
        )

    @staticmethod
    async def _drop_shortlist(identifier: str):
        """
        Only use this method in a developer environment AND WHEN YOU'RE COMPLETELY SURE WHAT YOU ARE DOING!
        """
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id}, {"$set": {"short": []}}
        )

    @staticmethod
    async def _drop_algorithms(identifier: str):
        """
        Only use this method in a developer environment AND WHEN YOU'RE COMPLETELY SURE WHAT YOU ARE DOING!
        """
        UserRepository.list_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id}, {"$set": {"algorithms": []}}
        )
