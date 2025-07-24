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
        self.client = ArangoClient(hosts=settings.arango_url)
        self._ensure_database_exists()
        self.follow_db = self._connect_to_database()
        self.connections = self._create_collections()

    def _ensure_database_exists(self):
        system_db = self.client.db(
            "_system",
            username=settings.arango_user,
            password=settings.arango_password,
        )
        if not system_db.has_database(self.db_name):
            system_db.create_database(self.db_name)

    def _connect_to_database(self):
        return self.client.db(
            self.db_name,
            username=settings.arango_user,
            password=settings.arango_password,
        )

    def _create_collections(
        self,
        collections: tuple[CollectionTypes, ...] = (
            CollectionTypes.users,
            CollectionTypes.follows,
        ),
    ):
        result: dict[str, Union[StandardCollection, EdgeCollection]] = {}

        for collection in collections:
            collection_name, is_edge = collection.value
            if not self.follow_db.has_collection(collection_name):
                self.follow_db.create_collection(collection_name, edge=is_edge)
            result[collection_name] = self.follow_db.collection(collection_name)

        return result


arango_db_helper = ArangoDBHelper(is_test_mode=True)
