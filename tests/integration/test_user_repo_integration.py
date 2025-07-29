# tests/integration/test_user_repo_integration.py

import pytest

from app import get_arango_db_helper
from app.arango_db_helper import CollectionTypes
from app.repositories.user_repo import UserRepository


@pytest.fixture()
def arango_helper():
    helper = get_arango_db_helper(is_test_mode=True)
    yield helper

    for coll in helper.collections.values():
        coll.truncate()


@pytest.fixture()
def user_repo(arango_helper):
    users_coll = arango_helper.collections[CollectionTypes.users.value[0]]
    users_coll.truncate()
    return UserRepository(user_coll=users_coll)


def test_create_and_check_user(user_repo):
    username = "test_user"
    user_repo.create_user(username)
    assert user_repo.user_exists(username) is True


def test_user_not_exists(user_repo):
    assert user_repo.user_exists("non_existing_user") is False


def test_create_user_twice(user_repo):
    username = "duplicate_user"
    user_repo.create_user(username)
    user_repo.create_user(username)
    assert user_repo.user_exists(username) is True


def test_invalid_username(user_repo):
    with pytest.raises(TypeError):
        user_repo.create_user("")
    with pytest.raises(TypeError):
        user_repo.create_user(None)
    with pytest.raises(TypeError):
        user_repo.user_exists("")
