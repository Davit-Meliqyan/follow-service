from datetime import datetime as dt, UTC

from arango.collection import StandardCollection, EdgeCollection
from arango.database import StandardDatabase

from app.arango_db_helper import arango_db_helper, CollectionTypes
from app.validators.username_validator import UserValidator


class FollowRepository:
    def __init__(
            self,
            user_coll: StandardCollection = None,
            follow_coll: EdgeCollection = None,
            db: StandardDatabase = None,
    ):
        if user_coll is None or follow_coll is None or db is None:
            print(arango_db_helper.connections)
            self.user_coll = arango_db_helper.connections[
                CollectionTypes.users.value[0]
            ]
            self.follow_coll = arango_db_helper.connections[
                CollectionTypes.follows.value[0]
            ]
            self.db = arango_db_helper.follow_db
        else:
            self.user_coll = user_coll
            self.follow_coll = follow_coll
            self.db = db

    def _user_exists(self, username: str) -> bool:
        # Check if user with this username exists
        return self.user_coll.has(username)

    def create_follow(self, follower: str, followed: str) -> dict:
        # Validate input usernames
        UserValidator.validate_username(follower)
        UserValidator.validate_username(followed)

        # Prevent following oneself
        if follower == followed:
            raise ValueError("Cannot follow oneself")

        print(f"[INFO] Creating follow: {follower} -> {followed}")

        # Make sure both users exist
        if not (self.user_coll.has(follower) and self.user_coll.has(followed)):
            print("[ERROR] One or both users not found.")
            raise ValueError("User not found")

        # Create unique key for the follow edge
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
        # Validate input usernames
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


follow_repo = FollowRepository()
