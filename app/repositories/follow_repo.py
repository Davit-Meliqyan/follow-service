from datetime import datetime as dt, UTC

from arango.collection import StandardCollection, EdgeCollection
from arango.database import StandardDatabase

from app import get_arango_db_helper
from app.validators.username_validator import UserValidator


class FollowRepository:
    def __init__(
            self,
            user_coll: StandardCollection = None,
            follow_coll: EdgeCollection = None,
            db: StandardDatabase = None,
            is_test_mode: bool = False,
    ):
        if user_coll is None or follow_coll is None or db is None:
            helper = get_arango_db_helper(is_test_mode=is_test_mode)
            self.user_coll = helper.get_collection("users")
            self.follow_coll = helper.get_collection("follows")
            self.db = helper.db
        else:
            self.user_coll = user_coll
            self.follow_coll = follow_coll
            self.db = db

    def _user_exists(self, username: str) -> bool:
        return self.user_coll.has(username)

    def create_follow(self, follower: str, followed: str) -> dict:
        UserValidator.validate_username(follower)
        UserValidator.validate_username(followed)

        if follower == followed:
            raise ValueError("Cannot follow oneself")

        print(f"[INFO] Creating follow: {follower} -> {followed}")

        if not (self._user_exists(follower) and self._user_exists(followed)):
            print("[ERROR] One or both users not found.")
            raise ValueError("User not found")

        edge_key = f"{follower}__{followed}"
        edge = {
            "_key": edge_key,
            "_from": f"users/{follower}",
            "_to": f"users/{followed}",
            "followedAt": dt.now(tz=UTC).isoformat(),
        }

        self.follow_coll.insert(edge, overwrite=True)
        print(f"[INFO] Follow saved: {edge_key}")
        return edge

    def get_followers(self, username: str) -> list[dict]:
        print(f"[INFO] Getting followers for '{username}'")

        query = """
        FOR v, e IN INBOUND @userDoc follows
            RETURN {
                followed: v.username,
                followedAt: e.followedAt
            }
        """
        cursor = self.db.aql.execute(query, bind_vars={"userDoc": f"users/{username}"})
        results = list(cursor)
        print(f"[INFO] Found {len(results)} followers.")
        return results

    def get_following(self, username: str) -> list[dict]:
        print(f"[INFO] Getting users followed by '{username}'")

        query = """
        FOR v, e IN OUTBOUND @userDoc follows
            RETURN {
                followed: v.username,
                followedAt: e.followedAt
            }
        """
        cursor = self.db.aql.execute(query, bind_vars={"userDoc": f"users/{username}"})
        results = list(cursor)
        print(f"[INFO] Found {len(results)} followed users.")
        return results

    def delete_follow(self, follower: str, followed: str) -> bool:
        UserValidator.validate_username(follower)
        UserValidator.validate_username(followed)

        edge_key = f"{follower}__{followed}"
        print(f"[INFO] Deleting follow: {follower} -> {followed}")

        if self.follow_coll.has(edge_key):
            self.follow_coll.delete(edge_key)
            print("[INFO] Follow deleted.")
            return True

        print("[INFO] Follow not found.")
        return False

    def count_followers(self, username: str) -> int:
        query = """
        RETURN LENGTH(
            FOR v IN 1..1 INBOUND @user follows
                RETURN 1
        )
        """
        cursor = self.db.aql.execute(query, bind_vars={"user": f"users/{username}"})
        count = next(cursor)
        print(f"[INFO] [{dt.now(tz=UTC).isoformat()}] User '{username}' has {count} followers.")
        return count

    def count_following(self, username: str) -> int:
        query = """
        RETURN LENGTH(
            FOR v IN 1..1 OUTBOUND @user follows
                RETURN 1
        )
        """
        cursor = self.db.aql.execute(query, bind_vars={"user": f"users/{username}"})
        count = next(cursor)
        print(f"[INFO] [{dt.now(tz=UTC).isoformat()}] User '{username}' is following {count} users.")
        return count
