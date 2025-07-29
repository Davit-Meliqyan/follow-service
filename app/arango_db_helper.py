from enum import Enum
from typing import Union

from arango.client import ArangoClient
from arango.collection import StandardCollection, EdgeCollection

from app.config import settings

class CollectionTypes(Enum):
    users = ("users", False)
    follows = ("follows", True)


class ArangoDBHelper:
    def __init__(self, is_test_mode: bool = False):
        self.db_name = (
            settings.test_arango_db if is_test_mode else settings.arango_db
        )
        mode = "TEST" if is_test_mode else "PRODUCTION"
        print(f"[INIT] Starting ArangoDBHelper in {mode} mode")
        print(f"[INIT] Target database: '{self.db_name}'")

        self.client = ArangoClient(hosts=settings.arango_url)

        self._ensure_database_exists()
        self.db = self._connect_to_database()
        self.collections = self._create_collections()

    def _ensure_database_exists(self):
        print("[CHECK] Ensuring database exists...")
        system_db = self.client.db(
            "_system",
            username=settings.arango_user,
            password=settings.arango_password,
        )
        if not system_db.has_database(self.db_name):
            print(f"[CREATE] Database '{self.db_name}' does not exist. Creating...")
            system_db.create_database(self.db_name)
        else:
            print(f"[OK] Database '{self.db_name}' already exists.")

    def _connect_to_database(self):
        print(f"[CONNECT] Connecting to database '{self.db_name}'...")
        db = self.client.db(
            self.db_name,
            username=settings.arango_user,
            password=settings.arango_password,
        )
        print(f"[OK] Connected to '{self.db_name}'")
        return db

    def _create_collections(
        self,
        collections: tuple[CollectionTypes, ...] = (
            CollectionTypes.users,
            CollectionTypes.follows,
        ),
    ):
        print("[COLLECTIONS] Ensuring required collections exist...")
        result: dict[str, Union[StandardCollection, EdgeCollection]] = {}

        for collection in collections:
            name, is_edge = collection.value
            if not self.db.has_collection(name):
                print(f"[CREATE] Collection '{name}' does not exist. Creating (edge={is_edge})...")
                self.db.create_collection(name, edge=is_edge)
            else:
                print(f"[OK] Collection '{name}' already exists.")
            result[name] = self.db.collection(name)

        return result

    def get_collection(self, name: str) -> Union[StandardCollection, EdgeCollection]:
        print(f"[ACCESS] Getting collection '{name}'")
        return self.collections[name]
