from unittest.mock import MagicMock

import pytest

from app.repositories.graph_traversal_repo import GraphTraversalRepository


@pytest.fixture
def mock_db():
    """Mock database with an 'aql.execute' attribute."""
    mock_db = MagicMock()
    return mock_db


@pytest.fixture
def graph_repo(mock_db):
    """GraphTraversalRepository instance with mocked database."""
    return GraphTraversalRepository(db=mock_db)


@pytest.fixture
def graph_repo_with_validation():
    """GraphTraversalRepository instance with no db (for validation tests)."""
    return GraphTraversalRepository(db=None)


def test_traverse_bfs_returns_expected_results(graph_repo, mock_db):
    # Arrange
    mock_cursor = iter([
        {"followed": "user1", "followed_at": "2025-07-15T12:00:00"},
        {"followed": "user2", "followed_at": "2025-07-15T13:00:00"},
    ])
    mock_db.aql.execute.return_value = mock_cursor

    # Act
    results = graph_repo.traverse_bfs("testuser", max_depth=2)

    # Assert
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["followed"] == "user1"
    assert results[1]["followed_at"] == "2025-07-15T13:00:00"
    mock_db.aql.execute.assert_called_once()

    print("[TEST] traverse_bfs returns expected results.")


def test_traverse_dfs_returns_expected_results(graph_repo, mock_db):
    # Arrange
    mock_cursor = iter([
        {"followed": "user3", "followed_at": "2025-07-16T10:00:00"}
    ])
    mock_db.aql.execute.return_value = mock_cursor

    # Act
    results = graph_repo.traverse_dfs("anotheruser", max_depth=1)

    # Assert
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["followed"] == "user3"
    mock_db.aql.execute.assert_called_once()

    print("[TEST] traverse_dfs returns expected results.")


def test_traverse_bfs_empty_result(graph_repo, mock_db):
    # Arrange
    mock_db.aql.execute.return_value = iter([])

    # Act
    results = graph_repo.traverse_bfs("no_followers", max_depth=3)

    # Assert
    assert results == []
    mock_db.aql.execute.assert_called_once()

    print("[TEST] traverse_bfs returns empty list when no results.")


def test_traverse_dfs_empty_result(graph_repo, mock_db):
    # Arrange
    mock_db.aql.execute.return_value = iter([])

    # Act
    results = graph_repo.traverse_dfs("no_following", max_depth=3)

    # Assert
    assert results == []
    mock_db.aql.execute.assert_called_once()

    print("[TEST] traverse_dfs returns empty list when no results.")


def test_traverse_bfs_invalid_username_type(graph_repo):
    # Act & Assert
    try:
        graph_repo.traverse_bfs(None)
    except TypeError:
        print("[TEST] traverse_bfs raises TypeError on invalid username type.")
    else:
        assert False, "Expected TypeError was not raised."


def test_traverse_dfs_invalid_max_depth_type(graph_repo):
    # Act & Assert
    try:
        graph_repo.traverse_dfs("user", max_depth="not_an_int")
    except TypeError:
        print("[TEST] traverse_dfs raises TypeError on invalid max_depth type.")
    else:
        assert False, "Expected TypeError was not raised."


def test_traverse_bfs_invalid_username_type_raises_type_error(graph_repo):
    with pytest.raises(TypeError, match="Username must be a non-empty string"):
        graph_repo.traverse_bfs(None)


def test_traverse_bfs_invalid_max_depth_type_raises_type_error(graph_repo):
    with pytest.raises(TypeError, match="max_depth must be an integer"):
        graph_repo.traverse_bfs("user", max_depth="not_an_int")


def test_traverse_dfs_invalid_username_type_raises_type_error(graph_repo):
    with pytest.raises(TypeError, match="Username must be a non-empty string"):
        graph_repo.traverse_dfs(123)


def test_traverse_dfs_invalid_max_depth_type_raises_type_error(graph_repo):
    with pytest.raises(TypeError, match="max_depth must be an integer"):
        graph_repo.traverse_dfs("user", max_depth=2.5)


def test_validate_input_raises_on_non_string_username():
    with pytest.raises(TypeError, match="Username must be a non-empty string"):
        GraphTraversalRepository._validate_input(123, 2)


def test_validate_input_raises_on_non_int_max_depth():
    with pytest.raises(TypeError, match="max_depth must be an integer"):
        GraphTraversalRepository._validate_input("user", "not_an_int")
