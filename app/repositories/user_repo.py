from arango.collection import StandardCollection

from app import get_arango_db_helper
from app.validators.username_validator import UserValidator


class UserRepository:
    def __init__(self, user_coll: StandardCollection = None, is_test_mode: bool = False):
        if user_coll is None:
            helper = get_arango_db_helper(is_test_mode=is_test_mode)
            user_coll = helper.get_collection("users")
        self.user_coll = user_coll

    def create_user(self, username: str) -> None:
        UserValidator.validate_username(username)

        if self.user_coll.has(username):
            print(f"[INFO] User '{username}' already exists.")
            return

        self.user_coll.insert({"_key": username, "username": username})
        print(f"[INFO] User '{username}' created.")

    def user_exists(self, username: str) -> bool:
        UserValidator.validate_username(username)
        exists = self.user_coll.has(username)
        print(f"[INFO] Exists check for '{username}': {exists}")
        return exists
