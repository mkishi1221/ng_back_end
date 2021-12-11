from api.event_handler import ConnectionManager
from ...user_repository.repository import UserRepository


class UserCacheMutations(UserRepository):
    ## keyword cache
    @staticmethod
    def add_keyword_to_cache(keyword: str, identifier: str):
        """
        Add a single keyword to the user keyword cache
        """
        return UserRepository.keyword_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier)},
            {"$addToSet": {"cache": keyword}},
            upsert=True,
        )

    @staticmethod
    def get_keyword_cache(identifier: str):
        """
        Read the user keyword cache
        """
        return UserRepository.keyword_collection.find_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id}
        )["cache"]

    ## sentence cache
    @staticmethod
    def add_sentence_to_cache(sentence: str, identifier: str):
        """
        Add a single sentence to the user sentence cache
        """
        return UserRepository.sentence_collection.update_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id},
            {"$addToSet": {"cache": sentence}},
            upsert=True,
        )

    @staticmethod
    def get_sentence_cache(identifier: str):
        """
        Read the user sentence cache
        """
        return UserRepository.sentence_collection.find_one(
            {"project_id": ConnectionManager.get_user(identifier).project_id}
        )["cache"]
