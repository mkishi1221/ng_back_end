from ...user_repository.repository import UserRepository


class ProjectsMutations(UserRepository):
    @staticmethod
    def add_project():
        UserRepository.project_collection.update_one(
            {"project_name": UserRepository.project}, {"$set": {
                "project_name": UserRepository.project,
                "users": [
                    UserRepository.username
                ]
            }}, upsert=True
        )
