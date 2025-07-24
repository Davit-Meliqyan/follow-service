# app/models.py
from pydantic import BaseModel


class FollowCreate(BaseModel):
    follower: str
    followed: str


class FollowOut(BaseModel):
    followed: str
    followed_at: str

    class Config:
        orm_mode = True