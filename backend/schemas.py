from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ========== 文章相关 ==========
class PostBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    category: Optional[str] = "其它"
    tags: Optional[str] = ""


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None


class Post(PostBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author_id: Optional[int] = None
    is_hidden: bool = False

    class Config:
        from_attributes = True


class PostPublic(PostBase):
    """前台展示的文章模型，包含作者名称"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author_id: Optional[int] = None
    author_name: Optional[str] = None

    class Config:
        from_attributes = True


# ========== 用户相关 ==========
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_superuser: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str


# ========== Token 相关 ==========
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
