from enum import Enum
from typing import Union

from arango.client import ArangoClient
from arango.collection import StandardCollection, EdgeCollection

from app.config import settings

client = ArangoClient(hosts=settings.arango_url)


class CollectionTypes(Enum):
    users = "users", False
    follows = "follows", True


class ArangoDBHelper:

    def __init__(self, is_test_mode: bool = False):
        system_db = client.db(
            "_system",
            username=settings.arango_user,
            password=settings.arango_password,
        )

        if not is_test_mode:

            if not system_db.has_database(settings.arango_db):
                system_db.create_database(settings.arango_db)
            self.follow_db = client.db(
                settings.arango_db,
                username=settings.arango_user,
                password=settings.arango_password,
            )
        else:
            if not system_db.has_database(settings.test_arango_db):
                system_db.create_database(
                    settings.test_arango_db,
                )
            self.follow_db = client.db(
                settings.test_arango_db,
                username=settings.arango_user,
                password=settings.arango_password,
            )

        self.connections = self._create_collections()

    def _create_collections(
        self,
        collections: tuple[CollectionTypes] = (
            CollectionTypes.users,
            CollectionTypes.follows,
        ),
    ):
        _collections: dict[
            CollectionTypes, Union[StandardCollection, EdgeCollection]
        ] = {}

        for collection in collections:
            collection_name, is_edge = collection.value
            if not self.follow_db.has_collection(collection_name):
                self.follow_db.create_collection(collection_name, edge=is_edge)
            _collections[collection_name] = self.follow_db.collection(collection_name)

        return _collections


arango_db_helper = ArangoDBHelper(is_test_mode=True)
