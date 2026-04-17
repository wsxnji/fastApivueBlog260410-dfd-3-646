from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ========== 分类相关 ==========
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


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


class TagUpdate(BaseModel):
    name: Optional[str] = None


class Tag(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 评论相关 ==========
class CommentBase(BaseModel):
    content: str
    parent_id: Optional[int] = None


class CommentCreate(CommentBase):
    pass


class CommentAuthor(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Comment(CommentBase):
    id: int
    post_id: int
    author_id: int
    author: Optional[CommentAuthor] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    replies: List['Comment'] = []

    class Config:
        from_attributes = True


# 解决循环引用
Comment.model_rebuild()


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
    post: Optional['PostPublic'] = None

    class Config:
        from_attributes = True


# ========== 文章相关 ==========
class PostBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[str] = ""


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: Optional[int] = None
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
    """前台展示的文章模型，包含作者名称、点赞数、评论数、收藏数"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    category_name: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    favorites_count: int = 0
    is_liked_by_me: bool = False
    is_favorited_by_me: bool = False

    class Config:
        from_attributes = True


# 解决循环引用
Favorite.model_rebuild()


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
