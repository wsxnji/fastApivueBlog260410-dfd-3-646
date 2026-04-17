from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PostBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = []


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


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


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    parent_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: str


class CommentAuthor(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Comment(CommentBase):
    id: int
    post_id: int
    author_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: CommentAuthor
    replies: List['Comment'] = []

    class Config:
        from_attributes = True


Comment.model_rebuild()


class Post(PostBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author_id: Optional[int] = None
    is_hidden: bool = False
    category: Optional[Category] = None
    tags: List[Tag] = []

    class Config:
        from_attributes = True


class PostPublic(BaseModel):
    id: int
    title: str
    content: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    category: Optional[Category] = None
    tags: List[Tag] = []
    like_count: int = 0
    comment_count: int = 0
    is_liked: bool = False
    is_favorited: bool = False

    class Config:
        from_attributes = True


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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class FavoriteBase(BaseModel):
    post_id: int


class Favorite(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime
    post: PostPublic

    class Config:
        from_attributes = True
