# tests/unit/test_user_repo.py

import pytest
from unittest.mock import MagicMock
from app.repositories.user_repo import UserRepository


@pytest.fixture
def mock_collection():
    """Create a mock of the ArangoDB users collection."""
    return MagicMock()


@pytest.fixture
def user_repo(mock_collection):
    """Create a UserRepository instance with the mocked collection."""
    return UserRepository(user_coll=mock_collection)


def test_create_user_success(user_repo, mock_collection):
    """Test creating a new user when it does not exist."""
    username = "test_user"
    mock_collection.has.return_value = False

    user_repo.create_user(username)

    mock_collection.insert.assert_called_once_with({
        "_key": username,
        "username": username
    })
    print(f"[TEST] User '{username}' was successfully created.")


def test_create_user_already_exists(user_repo, mock_collection):
    """Test that existing user is not inserted again."""
    username = "existing_user"
    mock_collection.has.return_value = True

    user_repo.create_user(username)

    mock_collection.insert.assert_not_called()
    print(f"[TEST] User '{username}' already exists. Insert skipped.")


def test_user_exists_true(user_repo, mock_collection):
    """Test user_exists() returns True when user is found."""
    username = "user1"
    mock_collection.has.return_value = True

    result = user_repo.user_exists(username)

    assert result is True
    print(f"[TEST] user_exists('{username}') returned True as expected.")


def test_user_exists_false(user_repo, mock_collection):
    """Test user_exists() returns False when user is not found."""
    username = "user2"
    mock_collection.has.return_value = False

    result = user_repo.user_exists(username)

    assert result is False
    print(f"[TEST] user_exists('{username}') returned False as expected.")


def test_create_user_with_invalid_username(user_repo):
    """Test create_user with invalid input (e.g., None)."""
    with pytest.raises(TypeError):
        user_repo.create_user(None)
    print(f"[TEST] Creating user with None raised TypeError as expected.")


def test_user_exists_called_with_correct_argument(user_repo, mock_collection):
    """Ensure .has() is called with the correct username."""
    username = "exact_user"
    user_repo.user_exists(username)

    mock_collection.has.assert_called_once_with(username)
    print(f"[TEST] user_exists('{username}') called .has() correctly.")
