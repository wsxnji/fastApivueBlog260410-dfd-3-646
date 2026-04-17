from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from database import get_db
from crud import (
    get_post, get_posts, create_post, update_post, delete_post, toggle_post_hidden,
    create_user, get_user,
    get_categories, get_category, create_category, update_category, delete_category, get_category_by_name,
    get_tags, get_tag, create_tag, update_tag, delete_tag, get_tag_by_name,
    get_comments_by_post, build_comment_tree, create_comment, delete_comment, get_comment,
    get_like, get_like_count, create_like, delete_like,
    get_favorite, get_favorite_count, create_favorite, delete_favorite, get_favorites_by_user,
    get_posts_by_category, get_posts_by_tag, get_comment_count
)
from schemas import (
    Post, PostCreate, PostUpdate, PostPublic, User, UserCreate, Token,
    Category, CategoryCreate, CategoryUpdate,
    Tag, TagCreate, TagUpdate,
    Comment, CommentCreate
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
    from crud import get_user_by_username
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    return create_user(db=db, user=user, is_superuser=is_superuser)


# ========== 文章相关 ==========
@router.get("/posts", response_model=list[Post])
def read_posts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取文章列表（普通用户只能看到自己的文章，超级管理员可以看到所有文章）"""
    from crud import get_posts_by_author
    
    if current_user.is_superuser:
        # 超级管理员可以看到所有文章
        posts = get_posts(db, skip=skip, limit=limit)
    else:
        # 普通用户只能看到自己的文章
        posts = get_posts_by_author(db, author_id=current_user.id, skip=skip, limit=limit)
    
    return posts


@router.get("/posts/public", response_model=list[PostPublic])
def read_public_posts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取公开文章列表（前台展示，所有人可见）"""
    posts = get_posts(db, skip=skip, limit=limit)
    
    result = []
    for post in posts:
        post_dict = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "summary": post.summary,
            "cover": post.cover,
            "category_id": post.category_id,
            "category_name": post.category_name,
            "tags": post.tags,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "author_id": post.author_id,
            "author_name": None,
            "like_count": get_like_count(db, post.id),
            "favorite_count": get_favorite_count(db, post.id),
            "comment_count": get_comment_count(db, post.id),
            "is_liked": False,
            "is_favorited": False
        }
        if post.author_id:
            author = get_user(db, post.author_id)
            if author:
                post_dict["author_name"] = author.username
        if current_user:
            post_dict["is_liked"] = get_like(db, post.id, current_user.id) is not None
            post_dict["is_favorited"] = get_favorite(db, post.id, current_user.id) is not None
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
    
    post_dict = {
        "id": db_post.id,
        "title": db_post.title,
        "content": db_post.content,
        "summary": db_post.summary,
        "cover": db_post.cover,
        "category_id": db_post.category_id,
        "category_name": db_post.category_name,
        "tags": db_post.tags,
        "created_at": db_post.created_at,
        "updated_at": db_post.updated_at,
        "author_id": db_post.author_id,
        "author_name": None,
        "like_count": get_like_count(db, post_id),
        "favorite_count": get_favorite_count(db, post_id),
        "comment_count": get_comment_count(db, post_id),
        "is_liked": False,
        "is_favorited": False
    }
    if db_post.author_id:
        author = get_user(db, db_post.author_id)
        if author:
            post_dict["author_name"] = author.username
    if current_user:
        post_dict["is_liked"] = get_like(db, post_id, current_user.id) is not None
        post_dict["is_favorited"] = get_favorite(db, post_id, current_user.id) is not None
    
    return post_dict


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
    
    # 检查权限：普通用户只能更新自己的文章
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
    db_post = get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查权限：普通用户只能删除自己的文章
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


# ========== 分类管理（仅超级管理员） ==========
@router.get("/categories", response_model=list[Category])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    return get_categories(db, skip=skip, limit=limit)


@router.post("/categories", response_model=Category)
def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """创建分类（仅超级管理员）"""
    db_category = get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="分类已存在")
    return create_category(db=db, category=category)


@router.put("/categories/{category_id}", response_model=Category)
def update_existing_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """更新分类（仅超级管理员）"""
    db_category = get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    return update_category(db=db, category_id=category_id, category=category)


@router.delete("/categories/{category_id}")
def delete_existing_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """删除分类（仅超级管理员）"""
    db_category = get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    success = delete_category(db=db, category_id=category_id)
    return {"message": "分类删除成功"}


# ========== 标签管理（仅超级管理员） ==========
@router.get("/tags", response_model=list[Tag])
def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取标签列表"""
    return get_tags(db, skip=skip, limit=limit)


@router.post("/tags", response_model=Tag)
def create_new_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """创建标签（仅超级管理员）"""
    db_tag = get_tag_by_name(db, name=tag.name)
    if db_tag:
        raise HTTPException(status_code=400, detail="标签已存在")
    return create_tag(db=db, tag=tag)


@router.put("/tags/{tag_id}", response_model=Tag)
def update_existing_tag(
    tag_id: int,
    tag: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """更新标签（仅超级管理员）"""
    db_tag = get_tag(db, tag_id=tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="标签不存在")
    return update_tag(db=db, tag_id=tag_id, tag=tag)


@router.delete("/tags/{tag_id}")
def delete_existing_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """删除标签（仅超级管理员）"""
    db_tag = get_tag(db, tag_id=tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="标签不存在")
    success = delete_tag(db=db, tag_id=tag_id)
    return {"message": "标签删除成功"}


# ========== 按分类/标签筛选文章 ==========
@router.get("/posts/category/{category_name}", response_model=list[PostPublic])
def read_posts_by_category(
    category_name: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """按分类获取文章列表"""
    posts = get_posts_by_category(db, category_name=category_name, skip=skip, limit=limit)
    result = []
    for post in posts:
        post_dict = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "summary": post.summary,
            "cover": post.cover,
            "category_id": post.category_id,
            "category_name": post.category_name,
            "tags": post.tags,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "author_id": post.author_id,
            "author_name": None,
            "like_count": get_like_count(db, post.id),
            "favorite_count": get_favorite_count(db, post.id),
            "comment_count": get_comment_count(db, post.id),
            "is_liked": False,
            "is_favorited": False
        }
        if post.author_id:
            author = get_user(db, post.author_id)
            if author:
                post_dict["author_name"] = author.username
        result.append(post_dict)
    return result


@router.get("/posts/tag/{tag_name}", response_model=list[PostPublic])
def read_posts_by_tag(
    tag_name: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """按标签获取文章列表"""
    posts = get_posts_by_tag(db, tag_name=tag_name, skip=skip, limit=limit)
    result = []
    for post in posts:
        post_dict = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "summary": post.summary,
            "cover": post.cover,
            "category_id": post.category_id,
            "category_name": post.category_name,
            "tags": post.tags,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "author_id": post.author_id,
            "author_name": None,
            "like_count": get_like_count(db, post.id),
            "favorite_count": get_favorite_count(db, post.id),
            "comment_count": get_comment_count(db, post.id),
            "is_liked": False,
            "is_favorited": False
        }
        if post.author_id:
            author = get_user(db, post.author_id)
            if author:
                post_dict["author_name"] = author.username
        result.append(post_dict)
    return result


# ========== 评论系统 ==========
@router.get("/posts/{post_id}/comments")
def read_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    """获取文章评论列表（树形结构）"""
    comments = get_comments_by_post(db, post_id=post_id)
    return build_comment_tree(db, comments)


@router.post("/comments")
def create_new_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建评论"""
    db_post = get_post(db, post_id=comment.post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if comment.parent_id is None:
        if db_post.author_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="文章作者不能直接评论自己的文章，但可以回复他人评论"
            )
    else:
        parent_comment = get_comment(db, comment_id=comment.parent_id)
        if parent_comment is None:
            raise HTTPException(status_code=404, detail="父评论不存在")
    
    db_comment = create_comment(db=db, comment=comment, user_id=current_user.id)
    user = get_user(db, current_user.id)
    return {
        "id": db_comment.id,
        "post_id": db_comment.post_id,
        "user_id": db_comment.user_id,
        "parent_id": db_comment.parent_id,
        "content": db_comment.content,
        "username": user.username if user else "未知用户",
        "created_at": db_comment.created_at,
        "replies": []
    }


@router.delete("/comments/{comment_id}")
def delete_existing_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除评论（仅评论作者或管理员）"""
    db_comment = get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    if not current_user.is_superuser and db_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己的评论"
        )
    
    success = delete_comment(db=db, comment_id=comment_id)
    return {"message": "评论删除成功"}


# ========== 点赞功能 ==========
@router.post("/likes")
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """点赞/取消点赞"""
    db_post = get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if db_post.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="作者不能点赞自己的作品"
        )
    
    existing_like = get_like(db, post_id=post_id, user_id=current_user.id)
    if existing_like:
        delete_like(db, post_id=post_id, user_id=current_user.id)
        return {"message": "取消点赞成功", "liked": False, "count": get_like_count(db, post_id=post_id)}
    else:
        create_like(db, post_id=post_id, user_id=current_user.id)
        return {"message": "点赞成功", "liked": True, "count": get_like_count(db, post_id=post_id)}


@router.get("/posts/{post_id}/like-status")
def get_like_status(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户点赞状态"""
    liked = get_like(db, post_id=post_id, user_id=current_user.id) is not None
    return {"liked": liked, "count": get_like_count(db, post_id=post_id)}


# ========== 收藏功能 ==========
@router.post("/favorites")
def toggle_favorite(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """收藏/取消收藏"""
    db_post = get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    existing_favorite = get_favorite(db, post_id=post_id, user_id=current_user.id)
    if existing_favorite:
        delete_favorite(db, post_id=post_id, user_id=current_user.id)
        return {"message": "取消收藏成功", "favorited": False, "count": get_favorite_count(db, post_id=post_id)}
    else:
        create_favorite(db, post_id=post_id, user_id=current_user.id)
        return {"message": "收藏成功", "favorited": True, "count": get_favorite_count(db, post_id=post_id)}


@router.get("/favorites/me")
def read_my_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取我的收藏列表"""
    favorites = get_favorites_by_user(db, user_id=current_user.id)
    result = []
    for fav in favorites:
        post = get_post(db, post_id=fav.post_id)
        if post:
            author = get_user(db, post.author_id)
            post_dict = {
                "id": post.id,
                "title": post.title,
                "summary": post.summary,
                "cover": post.cover,
                "category_name": post.category_name,
                "created_at": post.created_at,
                "author_name": author.username if author else None,
                "favorite_id": fav.id
            }
            result.append(post_dict)
    return result


@router.get("/posts/{post_id}/favorite-status")
def get_favorite_status(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户收藏状态"""
    favorited = get_favorite(db, post_id=post_id, user_id=current_user.id) is not None
    return {"favorited": favorited, "count": get_favorite_count(db, post_id=post_id)}
