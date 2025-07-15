from unittest.mock import MagicMock

import pytest

from app.repositories.follow_repo import FollowRepository


# ---------- Fixtures ----------

@pytest.fixture
def mock_user_collection():
    # Mocked user document collection
    return MagicMock()


@pytest.fixture
def mock_follow_collection():
    # Mocked follow edge collection
    return MagicMock()


@pytest.fixture
def mock_db():
    # Mocked AQL-enabled database object
    return MagicMock()


@pytest.fixture
def follow_repo(mock_user_collection, mock_follow_collection, mock_db):
    # Create FollowRepository instance with mocks
    return FollowRepository(
        user_coll=mock_user_collection,
        follow_coll=mock_follow_collection,
        db=mock_db
    )


# ---------- Tests ----------

def test_create_follow_success(follow_repo, mock_user_collection, mock_follow_collection):
    """Test creating a follow edge between two existing users."""
    follower = "userA"
    followed = "userB"
    mock_user_collection.has.side_effect = lambda u: u in [follower, followed]

    result = follow_repo.create_follow(follower, followed)

    # Validate follow edge structure
    assert result["_key"] == f"{follower}__{followed}"
    assert result["_from"] == f"users/{follower}"
    assert result["_to"] == f"users/{followed}"
    assert "followedAt" in result
    mock_follow_collection.insert.assert_called_once()
    print("[TEST] Successfully tested create_follow with valid users.")


def test_create_follow_user_not_found(follow_repo, mock_user_collection):
    """Test that ValueError is raised if either user does not exist."""
    follower = "userX"
    followed = "userY"
    mock_user_collection.has.return_value = False

    with pytest.raises(ValueError, match="User not found"):
        follow_repo.create_follow(follower, followed)
    print("[TEST] Tested create_follow raises ValueError when user does not exist.")


def test_get_followers(follow_repo, mock_db):
    """Test get_followers returns correct list from AQL."""
    mock_cursor = [{"followed": "userA", "followed_at": "2024-01-01T12:00:00"}]
    mock_db.aql.execute.return_value = iter(mock_cursor)

    result = follow_repo.get_followers("userB")

    assert result == mock_cursor
    mock_db.aql.execute.assert_called_once()
    print("[TEST] Successfully tested get_followers.")


def test_get_following(follow_repo, mock_db):
    """Test get_following returns correct list from AQL."""
    mock_cursor = [{"followed": "userC", "followed_at": "2024-01-01T13:00:00"}]
    mock_db.aql.execute.return_value = iter(mock_cursor)

    result = follow_repo.get_following("userA")

    assert result == mock_cursor
    mock_db.aql.execute.assert_called_once()
    print("[TEST] Successfully tested get_following.")


def test_delete_follow_success(follow_repo, mock_follow_collection):
    """Test successful deletion of existing follow edge."""
    follower = "userA"
    followed = "userB"
    edge_key = f"{follower}__{followed}"
    mock_follow_collection.has.return_value = True

    result = follow_repo.delete_follow(follower, followed)

    assert result is True
    mock_follow_collection.delete.assert_called_once_with(edge_key)
    print("[TEST] Successfully tested delete_follow when edge exists.")


def test_delete_follow_not_found(follow_repo, mock_follow_collection):
    """Test delete_follow returns False if edge does not exist."""
    follower = "userA"
    followed = "userB"
    mock_follow_collection.has.return_value = False

    result = follow_repo.delete_follow(follower, followed)

    assert result is False
    mock_follow_collection.delete.assert_not_called()
    print("[TEST] Successfully tested delete_follow when edge does not exist.")


def test_create_follow_overwrites_existing(follow_repo, mock_user_collection, mock_follow_collection):
    """Test that repeated create_follow calls overwrite the edge."""
    follower = "userA"
    followed = "userB"
    mock_user_collection.has.side_effect = lambda u: u in [follower, followed]

    follow_repo.create_follow(follower, followed)
    follow_repo.create_follow(follower, followed)

    assert mock_follow_collection.insert.call_count == 2
    print("[TEST] Successfully tested create_follow overwrites existing edge.")


def test_create_follow_edge_key_formatting(follow_repo, mock_user_collection, mock_follow_collection):
    """Test that edge _key formatting handles special characters."""
    follower = "user-1"
    followed = "user.2"
    mock_user_collection.has.side_effect = lambda u: u in [follower, followed]

    edge = follow_repo.create_follow(follower, followed)

    assert edge["_key"] == f"{follower}__{followed}"
    print("[TEST] Successfully tested edge key formatting with special characters.")


def test_get_followers_empty(follow_repo, mock_db):
    """Test get_followers returns empty list when no data found."""
    mock_db.aql.execute.return_value = iter([])

    result = follow_repo.get_followers("userZ")

    assert result == []
    print("[TEST] Successfully tested get_followers with no followers.")


def test_get_following_empty(follow_repo, mock_db):
    """Test get_following returns empty list when no data found."""
    mock_db.aql.execute.return_value = iter([])

    result = follow_repo.get_following("userZ")

    assert result == []
    print("[TEST] Successfully tested get_following with no followed users.")


def test_delete_follow_same_user(follow_repo, mock_follow_collection):
    """Test delete_follow works if follower == followed (self-follow)."""
    user = "userX"
    mock_follow_collection.has.return_value = True

    result = follow_repo.delete_follow(user, user)

    assert result is True
    print("[TEST] Successfully tested delete_follow with same follower and followed (self-follow).")


def test_create_follow_with_same_user(follow_repo, mock_user_collection):
    """Test that following oneself raises ValueError (invalid follow)."""
    user = "sameUser"
    mock_user_collection.has.return_value = True

    with pytest.raises(ValueError, match="Cannot follow oneself"):
        follow_repo.create_follow(user, user)
    print("[TEST] Tested create_follow with same follower and followed user.")


def test_create_follow_with_invalid_username(follow_repo, mock_user_collection):
    """Test create_follow with invalid input like None or empty strings."""
    mock_user_collection.has.return_value = True

    with pytest.raises(TypeError):
        follow_repo.create_follow(None, "validUser")

    with pytest.raises(TypeError):
        follow_repo.create_follow("validUser", None)

    with pytest.raises(TypeError):
        follow_repo.create_follow("", "anotherUser")

    with pytest.raises(TypeError):
        follow_repo.create_follow("anotherUser", "")

    print("[TEST] Tested create_follow with invalid usernames like None or empty strings.")


def test_get_followers_query_format(follow_repo, mock_db):
    """Test that the AQL query for getting followers is structured correctly."""
    mock_db.aql.execute.return_value = iter([])

    follow_repo.get_followers("userQ")

    called_query = mock_db.aql.execute.call_args[0][0]
    assert "INBOUND" in called_query
    assert "follows" in called_query
    print("[TEST] Verified query format for get_followers contains 'INBOUND' and 'follows'.")


def test_get_following_query_format(follow_repo, mock_db):
    """Test that the AQL query for getting following is structured correctly."""
    mock_db.aql.execute.return_value = iter([])

    follow_repo.get_following("userW")

    called_query = mock_db.aql.execute.call_args[0][0]
    assert "OUTBOUND" in called_query
    assert "follows" in called_query
    print("[TEST] Verified query format for get_following contains 'OUTBOUND' and 'follows'.")


def test_delete_follow_invalid_users(follow_repo, mock_follow_collection):
    """Test delete_follow with invalid inputs like None or empty usernames."""
    with pytest.raises(TypeError):
        follow_repo.delete_follow(None, "userB")

    with pytest.raises(TypeError):
        follow_repo.delete_follow("userA", None)

    with pytest.raises(TypeError):
        follow_repo.delete_follow("", "userB")

    with pytest.raises(TypeError):
        follow_repo.delete_follow("userA", "")

    print("[TEST] Tested delete_follow with invalid inputs like None or empty strings.")


def test_create_follow_insert_called_with_expected_data(follow_repo, mock_user_collection, mock_follow_collection):
    """Test that insert is called with a correctly formed edge document."""
    follower = "alpha"
    followed = "beta"
    mock_user_collection.has.side_effect = lambda u: u in [follower, followed]

    follow_repo.create_follow(follower, followed)

    inserted_doc = mock_follow_collection.insert.call_args[0][0]
    assert inserted_doc["_key"] == "alpha__beta"
    assert inserted_doc["_from"] == "users/alpha"
    assert inserted_doc["_to"] == "users/beta"
    assert "followedAt" in inserted_doc
    print("[TEST] Verified insert data structure in create_follow.")
