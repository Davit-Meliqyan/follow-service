import pytest
from testcontainers.arangodb import ArangoDbContainer
from arango import ArangoClient

from app.repositories.user_repo import UserRepository


@pytest.fixture(scope="module")
def arango_container():
    print("[LOG] Starting ArangoDB test container...")
    with ArangoDbContainer("arangodb:latest") as container:
        container.with_env("ARANGO_ROOT_PASSWORD", "1234")
        container.start()

        url = f"http://{container.get_container_host_ip()}:{container.get_exposed_port(8529)}"
        print(f"[LOG] ArangoDB container started at {url}")
        yield {
            "url": url,
            "username": "root",
            "password": "test"
        }
    print("[LOG] ArangoDB test container stopped.")


@pytest.fixture
def user_repo_with_temp_db(arango_container):
    client = ArangoClient(hosts=arango_container["url"])
    db_name = "test_db"
    sys_db = client.db("_system", username=arango_container["username"], password=arango_container["password"])
    if not sys_db.has_database(db_name):
        print(f"[LOG] Creating test database '{db_name}'...")
        sys_db.create_database(db_name)
    else:
        print(f"[LOG] Test database '{db_name}' already exists.")

    db = client.db(db_name, username=arango_container["username"], password=arango_container["password"])
    if not db.has_collection("users"):
        print("[LOG] Creating 'users' collection...")
        db.create_collection("users")
    else:
        print("[LOG] 'users' collection already exists.")

    return UserRepository(user_coll=db.collection("users"))


def test_create_user_success(user_repo_with_temp_db):
    print("[TEST LOG] Running test_create_user_success...")
    repo = user_repo_with_temp_db

    username = "alice"
    repo.create_user(username)
    exists = repo.user_exists(username)
    print(f"[TEST LOG] User '{username}' created: exists={exists}")

    assert exists is True


def test_create_user_already_exists(user_repo_with_temp_db):
    print("[TEST LOG] Running test_create_user_already_exists...")
    repo = user_repo_with_temp_db

    username = "bob"
    repo.create_user(username)
    repo.create_user(username)  # Create again

    exists = repo.user_exists(username)
    print(f"[TEST LOG] User '{username}' created twice: exists={exists}")

    assert exists is True


def test_user_exists_false(user_repo_with_temp_db):
    print("[TEST LOG] Running test_user_exists_false...")
    repo = user_repo_with_temp_db

    username = "nonexistent_user"
    exists = repo.user_exists(username)
    print(f"[TEST LOG] User '{username}' existence check: exists={exists}")

    assert exists is False
