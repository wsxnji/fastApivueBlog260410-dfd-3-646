from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from crud import get_post, get_posts, create_post, update_post, delete_post, create_user, toggle_post_hidden
from schemas import Post, PostCreate, PostUpdate, PostPublic, User, UserCreate, Token
from auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_superuser,
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
def read_public_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """获取公开文章列表（前台展示，所有人可见）"""
    from crud import get_user
    posts = get_posts(db, skip=skip, limit=limit)
    
    # 为每篇文章添加作者名称
    result = []
    for post in posts:
        post_dict = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "summary": post.summary,
            "category": post.category,
            "tags": post.tags,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "author_id": post.author_id,
            "author_name": None
        }
        if post.author_id:
            author = get_user(db, post.author_id)
            if author:
                post_dict["author_name"] = author.username
        result.append(post_dict)
    
    return result


@router.get("/posts/{post_id}", response_model=PostPublic)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """获取单篇文章（公开）"""
    from crud import get_user
    db_post = get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 构建返回数据，包含作者名称
    post_dict = {
        "id": db_post.id,
        "title": db_post.title,
        "content": db_post.content,
        "summary": db_post.summary,
        "category": db_post.category,
        "tags": db_post.tags,
        "created_at": db_post.created_at,
        "updated_at": db_post.updated_at,
        "author_id": db_post.author_id,
        "author_name": None
    }
    if db_post.author_id:
        author = get_user(db, db_post.author_id)
        if author:
            post_dict["author_name"] = author.username
    
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
