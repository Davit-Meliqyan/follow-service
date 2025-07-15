from arango.database import StandardDatabase
from app.db import db


class GraphTraversalRepository:
    def __init__(self, db: StandardDatabase):
        self.db = db

    @staticmethod
    def _validate_username(username: str):
        # Validate that username is a non-empty string
        if not isinstance(username, str) or not username.strip():
            raise TypeError("Username must be a non-empty string")


    @staticmethod
    def _validate_max_depth(max_depth: int):
        # Validate that max_depth is an integer
        if not isinstance(max_depth, int):
            raise TypeError("max_depth must be an integer")

    @classmethod
    def _validate_input(cls, username: str, max_depth: int):
        # Call separate validation methods
        cls._validate_username(username)
        cls._validate_max_depth(max_depth)


    def traverse_bfs(self, username: str, max_depth: int = 3) -> list[dict]:
        self._validate_input(username, max_depth)

        print(f"[INFO] BFS traversal from '{username}', max depth = {max_depth}")
        query = """
          FOR v, e, p IN 1..@maxDepth OUTBOUND @userKey follows
              OPTIONS { bfs: true, uniqueVertices: 'global' }
              RETURN {
                  followed: v.username,
                  followedAt: e.followedAt
              }
          """
        cursor = self.db.aql.execute(
            query,
            bind_vars={"userKey": f"users/{username}", "maxDepth": max_depth}
        )
        results = list(cursor)
        print(f"[INFO] BFS traversal found {len(results)} users.")
        return results

    def traverse_dfs(self, username: str, max_depth: int = 3) -> list[dict]:
        self._validate_input(username, max_depth)

        print(f"[INFO] DFS traversal from '{username}', max depth = {max_depth}")
        query = """
          FOR v, e, p IN 1..@maxDepth OUTBOUND @userKey follows
              OPTIONS { bfs: false, uniqueVertices: 'path' }
              RETURN {
                  followed: v.username,
                  followedAt: e.followedAt
              }
          """
        cursor = self.db.aql.execute(
            query,
            bind_vars={"userKey": f"users/{username}", "maxDepth": max_depth}
        )
        results = list(cursor)
        print(f"[INFO] DFS traversal found {len(results)} users.")
        return results


graph_traversal_repo = GraphTraversalRepository(db=db)
