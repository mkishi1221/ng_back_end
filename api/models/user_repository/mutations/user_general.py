from ...user_repository.repository import UserRepository
from typing import Union
from ...user import User


class UserGeneralMutations(UserRepository):
    @staticmethod
    def create_user(username: str, pw: str):
        return UserRepository.user_cache_db.command(
            "createUser", username, pwd=pw, roles=["defaultUser"]
        )

    @staticmethod
    def change_user_pw(pw: str):
        return UserRepository.user_cache_db.command(
            "updateUser", UserRepository.project_id, pwd=pw
        )

    @staticmethod
    def get_user_by_name(username: str) -> Union[User, None]:
        user_dump = UserRepository.user_cache_db.command("usersInfo")
        users = list(
            map(lambda user: User(user["user"], user["userId"]), user_dump["users"])
        )
        return next((user for user in users if user.name == username), None)
