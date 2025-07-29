from fastapi import APIRouter, Query
from app.repositories import graph_traversal_repo
from app.models import FollowOut

router = APIRouter(
    prefix="/follow/traverse/bfs",
    tags=["Traversal - BFS"],
)

@router.get("/{username}", response_model=list[FollowOut])
async def traverse_bfs(username: str, depth: int = Query(3, ge=1, le=10)):
    records = graph_traversal_repo.traverse_bfs(username, max_depth=depth)
    return [
        FollowOut(
            followed=r.get("followed"),
            followed_at=r.get("followedAt", None)
        )
        for r in records
    ]