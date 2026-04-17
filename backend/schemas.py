from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ========== 分类相关 ==========
class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 标签相关 ==========
class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class Tag(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 文章相关 ==========
class PostBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    cover: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = "其它"
    tags: Optional[str] = ""


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    cover: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    tags: Optional[str] = None


class Post(PostBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author_id: Optional[int] = None
    is_hidden: bool = False
    like_count: Optional[int] = 0
    favorite_count: Optional[int] = 0
    comment_count: Optional[int] = 0

    class Config:
        from_attributes = True


class PostPublic(PostBase):
    """前台展示的文章模型，包含作者名称"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    like_count: Optional[int] = 0
    favorite_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    is_liked: Optional[bool] = False
    is_favorited: Optional[bool] = False

    class Config:
        from_attributes = True


# ========== 评论相关 ==========
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    post_id: int
    parent_id: Optional[int] = None


class Comment(CommentBase):
    id: int
    post_id: int
    user_id: int
    parent_id: Optional[int] = None
    username: str
    created_at: datetime
    replies: Optional[List["Comment"]] = []

    class Config:
        from_attributes = True


# ========== 点赞相关 ==========
class LikeBase(BaseModel):
    post_id: int


class LikeCreate(LikeBase):
    pass


class Like(LikeBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 收藏相关 ==========
class FavoriteBase(BaseModel):
    post_id: int


class FavoriteCreate(FavoriteBase):
    pass


class Favorite(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime

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
