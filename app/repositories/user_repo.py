from arango.collection import StandardCollection
from app.db import users


class UserRepository:
    def __init__(self, user_coll: StandardCollection = users):
        self.user_coll = user_coll

    def create_user(self, username: str):
        if not username:
            raise TypeError("Username must not be None or empty.")

        if self.user_coll.has(username):
            print(f"[INFO] User '{username}' already exists. Skipping creation.")
            return

        self.user_coll.insert({
            "_key": username,
            "username": username
        })
        print(f"[INFO] User '{username}' created successfully.")

    def user_exists(self, username: str) -> bool:
        exists = self.user_coll.has(username)
        print(f"[INFO] Checked existence for user '{username}': {exists}")
        return exists


user_repo = UserRepository()
