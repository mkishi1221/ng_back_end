from pymongo import MongoClient
from pymongo.errors import OperationFailure
from urllib.parse import quote_plus
import os


class UserRepository:

    client: MongoClient = MongoClient(
        f"mongodb://{quote_plus(os.environ['DB_ADMIN_USER'])}:{quote_plus(os.environ['DB_ADMIN_PASSWD'])}@199.231.189.38:27017/admin"
    )
    user_cache_db = client["user_cache"]

    # collections
    project_collection = user_cache_db.get_collection("projects")
    keyword_collection = user_cache_db.get_collection("keywords")
    sentence_collection = user_cache_db.get_collection("sentences")
    list_collection = user_cache_db.get_collection("lists")
    profile_collection = user_cache_db.get_collection("profiles")
    pricing_collection = user_cache_db.get_collection("pricing")

    @staticmethod
    def add_project(username: str, project: str):
        UserRepository.project_collection.update_one(
            {"project_name": project},
            {
                "$set": {
                    "project_name": project,
                    "users": [username],
                }
            },
            upsert=True,
        )

    @staticmethod
    def add_profile(username: str):
        UserRepository.profile_collection.update_one(
            {"user": username},
            {"$set": {"user": username, "last_project": ""}},
            upsert=True,
        )

    @staticmethod
    def init_user(username: str, project: str):

        profile_obj = UserRepository.profile_collection.find_one({"user": username})

        if not profile_obj:
            UserRepository.add_profile(username)
            profile_obj = UserRepository.profile_collection.find_one({"user": username})

        project_obj = UserRepository.project_collection.find_one(
            {"project_name": project, "users": {"$all": [username]}}
        )
        if not project_obj:
            UserRepository.add_project(username, project)
            project_obj = UserRepository.project_collection.find_one(
                {"project_name": project}
            )

        if not UserRepository.list_collection.find_one(
            {"project_id": project_obj["_id"]}
        ):
            UserRepository.list_collection.update_one(
                {"project_id": project_obj["_id"]},
                {
                    "$set": {
                        "project_id": project_obj["_id"],
                        "black": [],
                        "grey": [],
                        "white": [],
                        "short": [],
                        "algorithms": [],
                    }
                },
                upsert=True,
            )

        return project_obj["_id"]
