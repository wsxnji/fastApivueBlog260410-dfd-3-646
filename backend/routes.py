from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional, List
from database import get_db
from crud import (
    get_post, get_posts, create_post, update_post, delete_post, toggle_post_hidden,
    get_posts_by_author, get_posts_by_category, get_posts_by_tag,
    get_user, get_user_by_username, create_user,
    get_category, get_categories, create_category, update_category, delete_category,
    get_tag, get_tags, create_tag, update_tag, delete_tag,
    get_comments_by_post, create_comment, delete_comment,
    get_like, create_like, delete_like, get_likes_count,
    get_favorite, create_favorite, delete_favorite, get_favorites_by_user, get_favorites_count,
    get_post_stats
)
from schemas import (
    Post, PostCreate, PostUpdate, PostPublic, User, UserCreate, Token,
    Category, CategoryCreate, CategoryUpdate, Tag, TagCreate, TagUpdate,
    Comment, CommentCreate, Favorite
)
from auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_superuser,
    get_current_user_optional,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()


# ========== 认证相关 ==========
@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/auth/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user


# ========== 用户管理（仅超级管理员） ==========
@router.post("/users", response_model=User)
def create_new_user(
    user: UserCreate,
    is_superuser: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """创建新用户（仅超级管理员）"""
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    return create_user(db=db, user=user, is_superuser=is_superuser)


@router.get("/users", response_model=list[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """获取用户列表（仅超级管理员）"""
    return get_users(db, skip=skip, limit=limit)


# ========== 文章相关 ==========
@router.get("/posts", response_model=list[Post])
def read_posts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取文章列表（普通用户只能看到自己的文章，超级管理员可以看到所有文章）"""
    if current_user.is_superuser:
        posts = get_posts(db, skip=skip, limit=limit)
    else:
        posts = get_posts_by_author(db, author_id=current_user.id, skip=skip, limit=limit)
    return posts


@router.get("/posts/public", response_model=list[PostPublic])
def read_public_posts(
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取公开文章列表（前台展示，所有人可见）"""
    if category_id:
        posts = get_posts_by_category(db, category_id=category_id, skip=skip, limit=limit)
    elif tag:
        posts = get_posts_by_tag(db, tag=tag, skip=skip, limit=limit)
    else:
        posts = get_posts(db, skip=skip, limit=limit)
    
    result = []
    for post in posts:
        post_dict = build_post_public_dict(db, post, current_user.id if current_user else None)
        result.append(post_dict)
    
    return result


@router.get("/posts/{post_id}", response_model=PostPublic)
def read_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取单篇文章（公开）"""
    db_post = get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    return build_post_public_dict(db, db_post, current_user.id if current_user else None)


def build_post_public_dict(db: Session, post, current_user_id: Optional[int] = None) -> dict:
    """构建前台展示的文章数据"""
    author = get_user(db, post.author_id) if post.author_id else None
    category = get_category(db, post.category_id) if post.category_id else None
    stats = get_post_stats(db, post.id, current_user_id)
    
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "summary": post.summary,
        "cover_image": post.cover_image,
        "category_id": post.category_id,
        "category_name": category.name if category else None,
        "tags": post.tags,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "author_id": post.author_id,
        "author_name": author.username if author else None,
        **stats
    }


@router.post("/posts", response_model=Post)
def create_new_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建文章（需要登录）"""
    return create_post(db=db, post=post, author_id=current_user.id)


@router.put("/posts/{post_id}", response_model=Post)
def update_existing_post(
    post_id: int,
    post: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新文章（需要登录，超级管理员可更新所有文章，普通用户只能更新自己的文章）"""
    db_post = get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if not current_user.is_superuser:
        if db_post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能更新自己的文章"
            )
    
    db_post = update_post(db=db, post_id=post_id, post=post)
    return db_post


@router.delete("/posts/{post_id}")
def delete_existing_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除文章（需要登录，超级管理员可删除所有文章，普通用户只能删除自己的文章）"""
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if not current_user.is_superuser:
        if db_post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能删除自己的文章"
            )
    
    success = delete_post(db=db, post_id=post_id)
    return {"message": "文章删除成功"}


@router.patch("/posts/{post_id}/hidden")
def toggle_post_visibility(
    post_id: int,
    is_hidden: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """隐藏/显示文章（仅超级管理员）"""
    db_post = get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    db_post = toggle_post_hidden(db=db, post_id=post_id, is_hidden=is_hidden)
    action = "隐藏" if is_hidden else "显示"
    return {"message": f"文章已{action}", "post": db_post}


# ========== 分类相关（仅超级管理员） ==========
@router.get("/categories", response_model=list[Category])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取分类列表（公开）"""
    return get_categories(db, skip=skip, limit=limit)


@router.post("/categories", response_model=Category)
def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """创建分类（仅超级管理员）"""
    existing = get_category_by_name(db, category.name)
    if existing:
        raise HTTPException(status_code=400, detail="分类名称已存在")
    return create_category(db=db, category=category)


@router.put("/categories/{category_id}", response_model=Category)
def update_existing_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """更新分类（仅超级管理员）"""
    db_category = get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    if category.name:
        existing = get_category_by_name(db, category.name)
        if existing and existing.id != category_id:
            raise HTTPException(status_code=400, detail="分类名称已存在")
    
    return update_category(db=db, category_id=category_id, category=category)


@router.delete("/categories/{category_id}")
def delete_existing_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """删除分类（仅超级管理员）"""
    db_category = get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    success = delete_category(db=db, category_id=category_id)
    return {"message": "分类删除成功"}


# ========== 标签相关（仅超级管理员） ==========
@router.get("/tags", response_model=list[Tag])
def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取标签列表（公开）"""
    return get_tags(db, skip=skip, limit=limit)


@router.post("/tags", response_model=Tag)
def create_new_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """创建标签（仅超级管理员）"""
    existing = get_tag_by_name(db, tag.name)
    if existing:
        raise HTTPException(status_code=400, detail="标签名称已存在")
    return create_tag(db=db, tag=tag)


@router.put("/tags/{tag_id}", response_model=Tag)
def update_existing_tag(
    tag_id: int,
    tag: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """更新标签（仅超级管理员）"""
    db_tag = get_tag(db, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    if tag.name:
        existing = get_tag_by_name(db, tag.name)
        if existing and existing.id != tag_id:
            raise HTTPException(status_code=400, detail="标签名称已存在")
    
    return update_tag(db=db, tag_id=tag_id, tag=tag)


@router.delete("/tags/{tag_id}")
def delete_existing_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """删除标签（仅超级管理员）"""
    db_tag = get_tag(db, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    success = delete_tag(db=db, tag_id=tag_id)
    return {"message": "标签删除成功"}


# ========== 评论相关 ==========
@router.get("/posts/{post_id}/comments", response_model=list[Comment])
def read_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取文章的评论列表"""
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    comments = get_comments_by_post(db, post_id=post_id, skip=skip, limit=limit)
    return comments


@router.post("/posts/{post_id}/comments", response_model=Comment)
def create_new_comment(
    post_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建评论（需要登录）"""
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查是否是文章作者
    is_author = db_post.author_id == current_user.id
    
    # 如果是顶级评论（不是回复），作者不能评论自己的文章
    if comment.parent_id is None and is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="文章作者不能直接评论自己的文章"
        )
    
    # 如果是回复，检查父评论是否存在
    if comment.parent_id:
        parent_comment = db.query(Comment).filter(Comment.id == comment.parent_id).first()
        if parent_comment is None:
            raise HTTPException(status_code=404, detail="父评论不存在")
        if parent_comment.post_id != post_id:
            raise HTTPException(status_code=400, detail="父评论不属于当前文章")
    
    return create_comment(db=db, comment=comment, post_id=post_id, author_id=current_user.id)


@router.delete("/comments/{comment_id}")
def delete_existing_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除评论（需要登录，评论作者或超级管理员可删除）"""
    from models import Comment as CommentModel
    db_comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    # 检查权限：评论作者或超级管理员可删除
    if not current_user.is_superuser and db_comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己的评论"
        )
    
    success = delete_comment(db=db, comment_id=comment_id)
    return {"message": "评论删除成功"}


# ========== 点赞相关 ==========
@router.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """点赞文章（需要登录）"""
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 作者不能点赞自己的文章
    if db_post.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能点赞自己的文章"
        )
    
    # 检查是否已经点赞
    existing_like = get_like(db, post_id, current_user.id)
    if existing_like:
        raise HTTPException(status_code=400, detail="已经点赞过该文章")
    
    create_like(db=db, post_id=post_id, user_id=current_user.id)
    likes_count = get_likes_count(db, post_id)
    return {"message": "点赞成功", "likes_count": likes_count}


@router.delete("/posts/{post_id}/like")
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """取消点赞（需要登录）"""
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    success = delete_like(db=db, post_id=post_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="尚未点赞该文章")
    
    likes_count = get_likes_count(db, post_id)
    return {"message": "取消点赞成功", "likes_count": likes_count}


@router.get("/posts/{post_id}/like/status")
def check_like_status(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """检查当前用户是否点赞了文章"""
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    is_liked = get_like(db, post_id, current_user.id) is not None
    likes_count = get_likes_count(db, post_id)
    return {"is_liked": is_liked, "likes_count": likes_count}


# ========== 收藏相关 ==========
@router.post("/posts/{post_id}/favorite")
def favorite_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """收藏文章（需要登录）"""
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查是否已经收藏
    existing_favorite = get_favorite(db, post_id, current_user.id)
    if existing_favorite:
        raise HTTPException(status_code=400, detail="已经收藏过该文章")
    
    create_favorite(db=db, post_id=post_id, user_id=current_user.id)
    favorites_count = get_favorites_count(db, post_id)
    return {"message": "收藏成功", "favorites_count": favorites_count}


@router.delete("/posts/{post_id}/favorite")
def unfavorite_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """取消收藏（需要登录）"""
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    success = delete_favorite(db=db, post_id=post_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="尚未收藏该文章")
    
    favorites_count = get_favorites_count(db, post_id)
    return {"message": "取消收藏成功", "favorites_count": favorites_count}


@router.get("/posts/{post_id}/favorite/status")
def check_favorite_status(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """检查当前用户是否收藏了文章"""
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    is_favorited = get_favorite(db, post_id, current_user.id) is not None
    favorites_count = get_favorites_count(db, post_id)
    return {"is_favorited": is_favorited, "favorites_count": favorites_count}


@router.get("/favorites", response_model=list[Favorite])
def read_user_favorites(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的收藏列表"""
    favorites = get_favorites_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return favorites
