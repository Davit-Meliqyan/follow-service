import pytest

from app import get_arango_db_helper
from app.arango_db_helper import CollectionTypes
from app.repositories.follow_repo import FollowRepository
from app.repositories.user_repo import UserRepository


# --------- FIXTURES ---------

@pytest.fixture(scope="function")
def arango_helper():
    helper = get_arango_db_helper(is_test_mode=True)
    yield helper
    for name, coll in helper.collections.items():
        coll.truncate()
        print(f"[FIXTURE] Truncated collection: {name}")

@pytest.fixture()
def follow_repo(arango_helper):
    user_coll = arango_helper.collections[CollectionTypes.users.value[0]]
    follow_coll = arango_helper.collections[CollectionTypes.follows.value[0]]
    return FollowRepository(
        user_coll=user_coll,
        follow_coll=follow_coll,
        db=arango_helper.db
    )

@pytest.fixture()
def user_repo(arango_helper):
    users_coll = arango_helper.collections[CollectionTypes.users.value[0]]
    return UserRepository(user_coll=users_coll)


# --------- TEST CASES ---------

def test_create_and_query_follow(follow_repo, user_repo):
    # Create two users and a follow edge between them
    follower = "alice"
    followed = "bob"
    user_repo.create_user(follower)
    user_repo.create_user(followed)

    follow_repo.create_follow(follower, followed)

    followers = follow_repo.get_followers(followed)
    following = follow_repo.get_following(follower)

    print(f"[LOG] Followers of {followed}: {followers}")
    print(f"[LOG] Following by {follower}: {following}")

    assert any(f["followed"] == follower for f in followers)
    assert any(f["followed"] == followed for f in following)


def test_delete_follow_edge(follow_repo, user_repo):
    follower = "charlie"
    followed = "dave"
    user_repo.create_user(follower)
    user_repo.create_user(followed)

    follow_repo.create_follow(follower, followed)
    deleted = follow_repo.delete_follow(follower, followed)

    print(f"[LOG] Deleted follow edge: {deleted}")
    assert deleted is True

    # Attempt to delete again, should return False
    assert follow_repo.delete_follow(follower, followed) is False


def test_cannot_follow_nonexistent_user(follow_repo):
    # Should raise ValueError since users do not exist
    with pytest.raises(ValueError):
        follow_repo.create_follow("ghost", "phantom")


def test_cannot_follow_self(follow_repo, user_repo):
    user = "echo"
    user_repo.create_user(user)

    with pytest.raises(ValueError, match="Cannot follow oneself"):
        follow_repo.create_follow(user, user)


def test_invalid_usernames(follow_repo, user_repo):
    user_repo.create_user("valid")

    with pytest.raises(TypeError):
        follow_repo.create_follow(None, "valid")

    with pytest.raises(TypeError):
        follow_repo.create_follow("valid", None)

    with pytest.raises(TypeError):
        follow_repo.delete_follow("", "valid")

    with pytest.raises(TypeError):
        follow_repo.delete_follow("valid", "   ")


def test_duplicate_follow(follow_repo, user_repo):
    print("[TEST] Start test_duplicate_follow")

    user_repo.create_user("alice")
    user_repo.create_user("bob")

    # First follow
    follow_repo.create_follow("alice", "bob")
    print("alice followed bob")

    # Duplicate follow (should not raise an error)
    follow_repo.create_follow("alice", "bob")
    print("alice tried to follow bob again")

    # Fetch followers of bob
    followers = follow_repo.get_followers("bob")
    print("Followers of bob:", followers)

    # Check there is exactly one follower and it's alice
    assert len(followers) == 1, "Expected only one follower"
    assert followers[0]["followed"] == "alice", "Expected follower to be alice"

    print("[TEST] test_duplicate_follow passed")


def test_get_followers_and_following_empty(follow_repo, user_repo):
    user_repo.create_user("nobody")

    followers = follow_repo.get_followers("nobody")
    following = follow_repo.get_following("nobody")

    print(f"[LOG] Followers of nobody: {followers}")
    print(f"[LOG] Following of nobody: {following}")

    assert followers == []
    assert following == []


def test_follow_cycle(follow_repo, user_repo):
    print("[TEST] Starting follow cycle test")

    # Create users
    user_repo.create_user("user_a")
    user_repo.create_user("user_b")
    user_repo.create_user("user_c")
    print("[TEST] Created users: user_a, user_b, user_c")

    # Create follow cycle: A -> B -> C -> A
    follow_repo.create_follow("user_a", "user_b")
    follow_repo.create_follow("user_b", "user_c")
    follow_repo.create_follow("user_c", "user_a")
    print("[TEST] Created follow edges: user_a->user_b, user_b->user_c, user_c->user_a")

    # Check followers of user_a: should include user_c
    followers_of_a = follow_repo.get_followers("user_a")
    assert any(f["followed"] == "user_c" for f in followers_of_a), "[FAIL] user_c is not following user_a"
    print("[TEST] Verified: user_c follows user_a")

    # Check followers of user_b: should include user_a
    followers_of_b = follow_repo.get_followers("user_b")
    assert any(f["followed"] == "user_a" for f in followers_of_b), "[FAIL] user_a is not following user_b"
    print("[TEST] Verified: user_a follows user_b")

    # Check followers of user_c: should include user_b
    followers_of_c = follow_repo.get_followers("user_c")
    assert any(f["followed"] == "user_b" for f in followers_of_c), "[FAIL] user_b is not following user_c"
    print("[TEST] Verified: user_b follows user_c")

    print("[TEST] Follow cycle test passed successfully")
