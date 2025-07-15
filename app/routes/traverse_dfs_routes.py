from fastapi import APIRouter, Query
from app.repositories.graph_traversal_repo import graph_traversal_repo
from app.models import FollowOut

router = APIRouter(
    prefix="/follow/traverse/dfs",
    tags=["Traversal - DFS"],
)

@router.get("/{username}", response_model=list[FollowOut])
async def traverse_dfs(username: str, depth: int = Query(3, ge=1, le=10)):
    records = graph_traversal_repo.traverse_dfs(username, max_depth=depth)
    return [
        FollowOut(
            followed=r.get("followed"),
            followed_at=r.get("followedAt", None)
        )
        for r in records
    ]