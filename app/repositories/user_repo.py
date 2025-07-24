from arango.collection import StandardCollection

from app.arango_db_helper import arango_db_helper, CollectionTypes
from app.validators.username_validator import UserValidator


class UserRepository:
    def __init__(self, user_coll: StandardCollection = None):
        # Use provided collection or default from helper
        self.user_coll = user_coll or arango_db_helper.connections[
            CollectionTypes.users.value[0]
        ]

    def create_user(self, username: str) -> None:
        # Create user if not exists
        UserValidator.validate_username(username)

        if self.user_coll.has(username):
            print(f"[INFO] User '{username}' already exists.")
            return

        self.user_coll.insert({"_key": username, "username": username})
        print(f"[INFO] User '{username}' created.")

    def user_exists(self, username: str) -> bool:
        # Check if user exists
        UserValidator.validate_username(username)
        exists = self.user_coll.has(username)
        print(f"[INFO] Exists check for '{username}': {exists}")
        return exists


user_repo = UserRepository()
