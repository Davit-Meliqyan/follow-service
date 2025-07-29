from app import get_arango_db_helper
from app.repositories.follow_repo import FollowRepository
from app.repositories.graph_traversal_repo import GraphTraversalRepository
from app.repositories.user_repo import UserRepository

arango_helper = get_arango_db_helper(is_test_mode=False)
graph_traversal_repo = GraphTraversalRepository(db=arango_helper.db)

follow_repo = FollowRepository(
    user_coll=arango_helper.get_collection("users"),
    follow_coll=arango_helper.get_collection("follows"),
    db=arango_helper.db
)

user_repo = UserRepository(
    user_coll=arango_helper.get_collection("users")
)
