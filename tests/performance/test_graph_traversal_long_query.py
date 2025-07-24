import time

import pytest
from arango.database import StandardDatabase

from app.arango_db_helper import arango_db_helper
from app.repositories.graph_traversal_repo import GraphTraversalRepository


@pytest.fixture(scope="module")
def db() -> StandardDatabase:
    return arango_db_helper.follow_db


@pytest.fixture(scope="module")
def graph_traversal_repo(db) -> GraphTraversalRepository:
    return GraphTraversalRepository(db=db)


def test_long_running_query_timing(graph_traversal_repo):
    print("[TEST] Starting long-running query timing test...")

    query = """
        FOR i IN 1..10
          LET delay = SLEEP(3)
          RETURN i
    """

    print("[TEST] Submitting AQL query with intentional delay (3s x 10 = ~30s)...")
    start_time = time.time()

    # Execute the query
    cursor = graph_traversal_repo.db.aql.execute(query, stream=True, batch_size=1)

    results = []
    for idx, item in enumerate(cursor, start=1):
        results.append(item)
        current_time = time.time()
        elapsed = current_time - start_time
        print(f"[TEST] Received item {idx}, elapsed: {elapsed:.2f}s")

    end_time = time.time()
    total_duration = end_time - start_time
    print(f"[TEST] Query finished in {total_duration:.2f} seconds")

    # Assert query took approximately 30 seconds
    assert 25 <= total_duration <= 35, "[ASSERT FAILED] Query duration out of expected range (25–35s)"

    # Assert correct results
    assert results == list(range(1, 11)), "[ASSERT FAILED] Query results are incorrect"

    print("[TEST] Long-running query test PASSED ✅")


# Requires Arango server-side timeout settings, or separate test setup
def test_query_timeout_simulation(graph_traversal_repo):
    print("[TEST] Simulating query timeout (if supported)")

    query = """
        FOR i IN 1..1000
          LET delay = SLEEP(1)
          RETURN i
    """

    try:
        cursor = graph_traversal_repo.db.aql.execute(query, ttl=10)  # ttl simulates timeout window
        list(cursor)
        pytest.fail("Expected timeout did not occur")
    except Exception as e:
        print(f"[TEST] Caught exception as expected: {e}")

    print("[TEST] Query timeout test PASSED ✅ (if applicable)")
