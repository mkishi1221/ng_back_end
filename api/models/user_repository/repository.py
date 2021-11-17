from pymongo import MongoClient
from pymongo.errors import OperationFailure
from urllib.parse import quote_plus
import os


class UserRepository:

    client: MongoClient = MongoClient(
        f"mongodb://{quote_plus(os.environ['DB_USER'])}:{quote_plus(os.environ['DB_PASSWD'])}@199.231.189.38:27017/user_cache"
    )
    user_cache_db = client["user_cache"]

    try:
        username = user_cache_db.command("connectionStatus")["authInfo"][
            "authenticatedUsers"
        ][0]["user"]
    except OperationFailure:
        print("Error: tried to call user repository without init_user call!")
        exit()

    # collections
    project_collection = user_cache_db.get_collection("projects")
    keyword_collection = user_cache_db.get_collection("keywords")
    sentence_collection = user_cache_db.get_collection("sentences")
    list_collection = user_cache_db.get_collection("lists")
    profile_collection = user_cache_db.get_collection("profiles")
    pricing_collection = user_cache_db.get_collection("pricing")

    # project config
    project = os.environ["PROJECT_NAME"]
    project_id = None

    @staticmethod
    def add_project():
        UserRepository.project_collection.update_one(
            {"project_name": UserRepository.project},
            {
                "$set": {
                    "project_name": UserRepository.project,
                    "users": [UserRepository.username],
                }
            },
            upsert=True,
        )

    @staticmethod
    def init_user():

        # TODO: optimize the whole project setup once we are in a "real" api / frontend setting
        project_obj = UserRepository.project_collection.find_one(
            {"project_name": UserRepository.project}
        )
        if not project_obj:
            UserRepository.add_project()
            project_obj = UserRepository.project_collection.find_one(
                {"project_name": UserRepository.project}
            )
        UserRepository.project_id = project_obj["_id"]

        if not UserRepository.list_collection.find_one(
            {"project_id": UserRepository.project_id}
        ):
            UserRepository.list_collection.update_one(
                {"project_id": UserRepository.project_id},
                {
                    "$set": {
                        "project_id": UserRepository.project_id,
                        "black": [],
                        "grey": [],
                        "white": [],
                        "short": [],
                    }
                },
                upsert=True,
            )
