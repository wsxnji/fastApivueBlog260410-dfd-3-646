from sqlalchemy.orm import Session
from models import Post, User, Category, Tag, Comment, Like, Favorite
from schemas import PostCreate, PostUpdate, UserCreate, CategoryCreate, CategoryUpdate, TagCreate, TagUpdate, CommentCreate
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


# ========== 分类相关 ==========
def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    return db.query(Category).filter(Category.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    return db.query(Category).order_by(Category.created_at.desc()).offset(skip).limit(limit).all()


def create_category(db: Session, category: CategoryCreate) -> Category:
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category: CategoryUpdate) -> Optional[Category]:
    db_category = get_category(db, category_id)
    if db_category:
        update_data = category.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        db.commit()
        db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False


# ========== 标签相关 ==========
def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_tag_by_name(db: Session, name: str) -> Optional[Tag]:
    return db.query(Tag).filter(Tag.name == name).first()


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
    return db.query(Tag).order_by(Tag.created_at.desc()).offset(skip).limit(limit).all()


def create_tag(db: Session, tag: TagCreate) -> Tag:
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def update_tag(db: Session, tag_id: int, tag: TagUpdate) -> Optional[Tag]:
    db_tag = get_tag(db, tag_id)
    if db_tag:
        update_data = tag.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tag, field, value)
        db.commit()
        db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, tag_id: int) -> bool:
    db_tag = get_tag(db, tag_id)
    if db_tag:
        db.delete(db_tag)
        db.commit()
        return True
    return False


# ========== 评论相关 ==========
def get_comment(db: Session, comment_id: int) -> Optional[Comment]:
    return db.query(Comment).filter(Comment.id == comment_id).first()


def get_comments_by_post(db: Session, post_id: int) -> List[Comment]:
    comments = db.query(Comment).filter(Comment.post_id == post_id, Comment.parent_id == None).order_by(Comment.created_at.desc()).all()
    return comments


def build_comment_tree(db: Session, comments: List[Comment]) -> List[dict]:
    result = []
    for comment in comments:
        user = get_user(db, comment.user_id)
        comment_dict = {
            "id": comment.id,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "parent_id": comment.parent_id,
            "content": comment.content,
            "username": user.username if user else "未知用户",
            "created_at": comment.created_at,
            "replies": []
        }
        replies = db.query(Comment).filter(Comment.parent_id == comment.id).order_by(Comment.created_at.asc()).all()
        comment_dict["replies"] = build_comment_tree(db, replies)
        result.append(comment_dict)
    return result


def create_comment(db: Session, comment: CommentCreate, user_id: int) -> Comment:
    db_comment = Comment(**comment.model_dump(), user_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, comment_id: int) -> bool:
    db_comment = get_comment(db, comment_id)
    if db_comment:
        db.delete(db_comment)
        db.commit()
        return True
    return False


# ========== 点赞相关 ==========
def get_like(db: Session, post_id: int, user_id: int) -> Optional[Like]:
    return db.query(Like).filter(Like.post_id == post_id, Like.user_id == user_id).first()


def get_like_count(db: Session, post_id: int) -> int:
    return db.query(Like).filter(Like.post_id == post_id).count()


def create_like(db: Session, post_id: int, user_id: int) -> Like:
    db_like = Like(post_id=post_id, user_id=user_id)
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like


def delete_like(db: Session, post_id: int, user_id: int) -> bool:
    db_like = get_like(db, post_id, user_id)
    if db_like:
        db.delete(db_like)
        db.commit()
        return True
    return False


# ========== 收藏相关 ==========
def get_favorite(db: Session, post_id: int, user_id: int) -> Optional[Favorite]:
    return db.query(Favorite).filter(Favorite.post_id == post_id, Favorite.user_id == user_id).first()


def get_favorite_count(db: Session, post_id: int) -> int:
    return db.query(Favorite).filter(Favorite.post_id == post_id).count()


def get_favorites_by_user(db: Session, user_id: int) -> List[Favorite]:
    return db.query(Favorite).filter(Favorite.user_id == user_id).order_by(Favorite.created_at.desc()).all()


def create_favorite(db: Session, post_id: int, user_id: int) -> Favorite:
    db_favorite = Favorite(post_id=post_id, user_id=user_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


def delete_favorite(db: Session, post_id: int, user_id: int) -> bool:
    db_favorite = get_favorite(db, post_id, user_id)
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
        return True
    return False


# ========== 文章筛选相关 ==========
def get_posts_by_category(db: Session, category_name: str, skip: int = 0, limit: int = 10) -> List[Post]:
    return db.query(Post).filter(Post.category_name == category_name).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()


def get_posts_by_tag(db: Session, tag_name: str, skip: int = 0, limit: int = 10) -> List[Post]:
    return db.query(Post).filter(Post.tags.like(f"%{tag_name}%")).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()


def get_comment_count(db: Session, post_id: int) -> int:
    return db.query(Comment).filter(Comment.post_id == post_id).count()
