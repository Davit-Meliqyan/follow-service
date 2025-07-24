import pytest
from arango.database import StandardDatabase

from app.arango_db_helper import arango_db_helper
from app.repositories.graph_traversal_repo import GraphTraversalRepository

TEST_USER = "testuser"


@pytest.fixture(scope="module")
def db() -> StandardDatabase:
    return arango_db_helper.follow_db


@pytest.fixture(scope="module")
def repo(db) -> GraphTraversalRepository:
    return GraphTraversalRepository(db=db)


@pytest.fixture(scope="module", autouse=True)
def setup_test_data(db: StandardDatabase):
    users = db.collection("users")
    follows = db.collection("follows")

    # Clear collections before tests
    users.delete_match({})
    follows.delete_match({})

    # Insert test users
    users.insert({"_key": "testuser", "username": "testuser"})
    users.insert({"_key": "user1", "username": "user1"})
    users.insert({"_key": "user2", "username": "user2"})

    # Insert follow relationships: testuser -> user1 -> user2
    follows.insert({
        "_from": "users/testuser",
        "_to": "users/user1",
        "followedAt": "2024-01-01T00:00:00Z"
    })
    follows.insert({
        "_from": "users/user1",
        "_to": "users/user2",
        "followedAt": "2024-01-02T00:00:00Z"
    })

    yield

    # Cleanup after tests
    users.delete_match({})
    follows.delete_match({})


def test_traverse_bfs_returns_correct_users(repo: GraphTraversalRepository):
    print("[TEST] test_traverse_bfs_returns_correct_users")
    results = repo.traverse_bfs(username=TEST_USER, max_depth=2)
    usernames = [r["followed"] for r in results]
    assert "user1" in usernames
    assert "user2" in usernames
    assert len(results) == 2


def test_traverse_bfs_limited_depth(repo: GraphTraversalRepository):
    print("[TEST] test_traverse_bfs_limited_depth")
    results = repo.traverse_bfs(username=TEST_USER, max_depth=1)
    usernames = [r["followed"] for r in results]
    assert usernames == ["user1"]
    assert len(results) == 1


def test_traverse_bfs_no_follows(repo: GraphTraversalRepository, db: StandardDatabase):
    print("[TEST] test_traverse_bfs_no_follows")
    users = db.collection("users")
    users.insert({"_key": "lonely_user", "username": "lonely_user"})

    results = repo.traverse_bfs(username="lonely_user", max_depth=3)
    assert results == []

    users.delete("lonely_user")


def test_traverse_bfs_user_does_not_exist(repo: GraphTraversalRepository):
    print("[TEST] test_traverse_bfs_user_does_not_exist")
    results = repo.traverse_bfs(username="ghost", max_depth=2)
    assert results == []


def test_traverse_bfs_cycle_detection(repo: GraphTraversalRepository, db: StandardDatabase):
    print("[TEST] test_traverse_bfs_cycle_detection")
    follows = db.collection("follows")

    follows.insert({
        "_from": "users/user2",
        "_to": "users/testuser",
        "followedAt": "2024-01-03T00:00:00Z"
    })

    results = repo.traverse_bfs(username=TEST_USER, max_depth=3)
    usernames = {r["followed"] for r in results}
    assert "user1" in usernames
    assert "user2" in usernames
    assert len(usernames) == 2

    follows.delete_match({
        "_from": "users/user2",
        "_to": "users/testuser"
    })


def test_traverse_bfs_multiple_paths(repo: GraphTraversalRepository, db: StandardDatabase):
    print("[TEST] test_traverse_bfs_multiple_paths")
    follows = db.collection("follows")

    follows.insert({
        "_from": "users/testuser",
        "_to": "users/user2",
        "followedAt": "2024-01-04T00:00:00Z"
    })

    results = repo.traverse_bfs(username=TEST_USER, max_depth=2)
    usernames = [r["followed"] for r in results]
    assert usernames.count("user2") == 1

    follows.delete_match({
        "_from": "users/testuser",
        "_to": "users/user2"
    })


def test_traverse_dfs_returns_correct_users(repo: GraphTraversalRepository):
    print("[TEST] test_traverse_dfs_returns_correct_users")
    results = repo.traverse_dfs(username=TEST_USER, max_depth=2)
    usernames = [r["followed"] for r in results]
    assert "user1" in usernames
    assert "user2" in usernames
    assert len(results) == 2


def test_traverse_invalid_username_raises(repo: GraphTraversalRepository):
    print("[TEST] test_traverse_invalid_username_raises")
    with pytest.raises(TypeError):
        repo.traverse_bfs(username="", max_depth=2)

    with pytest.raises(TypeError):
        repo.traverse_dfs(username=None, max_depth=2)


def test_traverse_invalid_depth_raises(repo: GraphTraversalRepository):
    print("[TEST] test_traverse_invalid_depth_raises")
    with pytest.raises(TypeError):
        repo.traverse_bfs(username=TEST_USER, max_depth="2")

    with pytest.raises(TypeError):
        repo.traverse_dfs(username=TEST_USER, max_depth=None)
