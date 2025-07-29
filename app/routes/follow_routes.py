from fastapi import APIRouter, HTTPException, status

from app.models import FollowCreate, FollowOut
from app.repositories import follow_repo

router = APIRouter(
    prefix="/follow",
    tags=["Follow"],
    responses={404: {"description": "User or follow not found"}},
)


@router.post(
    "/",
    response_model=FollowOut,
    status_code=status.HTTP_201_CREATED,
    summary="Follow a user",
    description="Add a follow edge between two usernames.",
)
async def create_follow(payload: FollowCreate):
    try:
        edge = follow_repo.create_follow(payload.follower, payload.followed)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return FollowOut(
        followed=payload.followed,
        followed_at=edge["followedAt"],
    )


@router.get(
    "/followers/{username}",
    response_model=list[FollowOut],
    summary="Get followers",
    description="Return all users that follow the given username.",
)
async def get_followers(username: str):
    records = follow_repo.get_followers(username)
    return [
        FollowOut(
            followed=r["followed"],
            followed_at=r.get("followedAt", None)
        )
        for r in records
    ]


@router.get(
    "/following/{username}",
    response_model=list[FollowOut],
    summary="Get following",
    description="Return all users that the given username is following.",
)
async def get_following(username: str):
    records = follow_repo.get_following(username)
    return [
        FollowOut(
            followed=r["followed"],
            followed_at=r.get("followed_at", ""),
        )
        for r in records
    ]


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unfollow a user",
    description="Remove a follow edge between two usernames.",
)
async def delete_follow(payload: FollowCreate):
    removed = follow_repo.delete_follow(payload.follower, payload.followed)
    if not removed:
        raise HTTPException(status_code=404, detail="Follow relation not found")


# @router.get(
#     "/count/followers/{username}",
#     summary="Count followers",
#     description="Return number of users that follow the given username."
# )
# async def get_follower_count(username: str) -> dict:
#     count = follow_repo.count_followers(username)
#     return {"follower_count": count}
#
#
# @router.get(
#     "/count/following/{username}",
#     summary="Count following",
#     description="Return number of users that the given username is following."
# )
# async def get_following_count(username: str) -> dict:
#     count = follow_repo.count_following(username)
#     return {"following_count": count}
