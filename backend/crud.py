from sqlalchemy.orm import Session
from models import Post, User
from schemas import PostCreate, PostUpdate, UserCreate
from auth import get_password_hash
from typing import List, Optional


# ========== 文章相关 ==========
def get_post(db: Session, post_id: int) -> Optional[Post]:
    return db.query(Post).filter(Post.id == post_id).first()


def get_posts(db: Session, skip: int = 0, limit: int = 10) -> List[Post]:
    return db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()


def get_posts_by_author(db: Session, author_id: int, skip: int = 0, limit: int = 10) -> List[Post]:
    return db.query(Post).filter(Post.author_id == author_id).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()


def create_post(db: Session, post: PostCreate, author_id: Optional[int] = None) -> Post:
    db_post = Post(**post.model_dump(), author_id=author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def update_post(db: Session, post_id: int, post: PostUpdate) -> Optional[Post]:
    db_post = get_post(db, post_id)
    if db_post:
        update_data = post.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_post, field, value)
        db.commit()
        db.refresh(db_post)
    return db_post


def toggle_post_hidden(db: Session, post_id: int, is_hidden: bool) -> Optional[Post]:
    db_post = get_post(db, post_id)
    if db_post:
        db_post.is_hidden = is_hidden
        db.commit()
        db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int) -> bool:
    db_post = get_post(db, post_id)
    if db_post:
        db.delete(db_post)
        db.commit()
        return True
    return False


# ========== 用户相关 ==========
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate, is_superuser: bool = False) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        is_superuser=is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data: dict) -> Optional[User]:
    db_user = get_user(db, user_id)
    if db_user:
        for field, value in user_data.items():
            if field == "password":
                setattr(db_user, "hashed_password", get_password_hash(value))
            else:
                setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
