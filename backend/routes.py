from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from database import get_db
import crud
from schemas import (
    Post, PostCreate, PostUpdate, PostPublic, User, UserCreate, Token,
    Category, CategoryCreate, CategoryUpdate,
    Tag, TagCreate, TagUpdate,
    Comment, CommentCreate, CommentUpdate,
    Favorite
)
from auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_user_optional,
    get_current_superuser,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
import os
import uuid
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    return current_user


@router.post("/users", response_model=User)
def create_new_user(
    user: UserCreate,
    is_superuser: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    return crud.create_user(db=db, user=user, is_superuser=is_superuser)


@router.get("/posts", response_model=list[Post])
def read_posts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.is_superuser:
        posts = crud.get_posts(db, skip=skip, limit=limit)
    else:
        posts = crud.get_posts_by_author(db, author_id=current_user.id, skip=skip, limit=limit)
    return posts


@router.get("/posts/public", response_model=list[PostPublic])
def read_public_posts(
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    posts = crud.get_posts(db, skip=skip, limit=limit, category_id=category_id, tag_id=tag_id)
    result = []
    for post in posts:
        author = crud.get_user(db, post.author_id) if post.author_id else None
        like_count = crud.get_like_count(db, post.id)
        comment_count = crud.get_comment_count(db, post.id)
        
        post_dict = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "summary": post.summary,
            "cover_image": post.cover_image,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "author_id": post.author_id,
            "author_name": author.username if author else None,
            "category": post.category,
            "tags": post.tags,
            "like_count": like_count,
            "comment_count": comment_count,
            "is_liked": False,
            "is_favorited": False
        }
        result.append(post_dict)
    return result


@router.get("/posts/{post_id}", response_model=PostPublic)
def read_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    author = crud.get_user(db, db_post.author_id) if db_post.author_id else None
    like_count = crud.get_like_count(db, db_post.id)
    comment_count = crud.get_comment_count(db, db_post.id)
    
    is_liked = False
    is_favorited = False
    if current_user:
        is_liked = crud.get_like(db, db_post.id, current_user.id) is not None
        is_favorited = crud.get_favorite(db, db_post.id, current_user.id) is not None
    
    return {
        "id": db_post.id,
        "title": db_post.title,
        "content": db_post.content,
        "summary": db_post.summary,
        "cover_image": db_post.cover_image,
        "created_at": db_post.created_at,
        "updated_at": db_post.updated_at,
        "author_id": db_post.author_id,
        "author_name": author.username if author else None,
        "category": db_post.category,
        "tags": db_post.tags,
        "like_count": like_count,
        "comment_count": comment_count,
        "is_liked": is_liked,
        "is_favorited": is_favorited
    }


@router.post("/posts", response_model=Post)
def create_new_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return crud.create_post(db=db, post=post, author_id=current_user.id)


@router.put("/posts/{post_id}", response_model=Post)
def update_existing_post(
    post_id: int,
    post: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if not current_user.is_superuser and db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能更新自己的文章"
        )
    
    return crud.update_post(db=db, post_id=post_id, post=post)


@router.delete("/posts/{post_id}")
def delete_existing_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if not current_user.is_superuser and db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己的文章"
        )
    
    crud.delete_post(db=db, post_id=post_id)
    return {"message": "文章删除成功"}


@router.patch("/posts/{post_id}/hidden")
def toggle_post_visibility(
    post_id: int,
    is_hidden: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    db_post = crud.toggle_post_hidden(db=db, post_id=post_id, is_hidden=is_hidden)
    action = "隐藏" if is_hidden else "显示"
    return {"message": f"文章已{action}", "post": db_post}


@router.get("/categories", response_model=list[Category])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_categories(db, skip=skip, limit=limit)


@router.post("/categories", response_model=Category)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    db_category = crud.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="分类名称已存在")
    return crud.create_category(db=db, category=category)


@router.put("/categories/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    db_category = crud.get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return crud.update_category(db=db, category_id=category_id, category=category)


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    success = crud.delete_category(db=db, category_id=category_id)
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"message": "分类删除成功"}


@router.get("/tags", response_model=list[Tag])
def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_tags(db, skip=skip, limit=limit)


@router.post("/tags", response_model=Tag)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    db_tag = crud.get_tag_by_name(db, name=tag.name)
    if db_tag:
        raise HTTPException(status_code=400, detail="标签名称已存在")
    return crud.create_tag(db=db, tag=tag)


@router.put("/tags/{tag_id}", response_model=Tag)
def update_tag(
    tag_id: int,
    tag: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    db_tag = crud.get_tag(db, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return crud.update_tag(db=db, tag_id=tag_id, tag=tag)


@router.delete("/tags/{tag_id}")
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    success = crud.delete_tag(db=db, tag_id=tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="标签不存在")
    return {"message": "标签删除成功"}


@router.get("/posts/{post_id}/comments", response_model=list[Comment])
def read_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_comments_by_post(db, post_id=post_id)


@router.post("/posts/{post_id}/comments", response_model=Comment)
def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_post = crud.get_post(db, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if db_post.author_id == current_user.id and not comment.parent_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="作者不能评论自己的文章，但可以回复他人的评论"
        )
    
    if comment.parent_id:
        parent_comment = crud.get_comment(db, comment.parent_id)
        if not parent_comment or parent_comment.post_id != post_id:
            raise HTTPException(status_code=400, detail="回复的评论不存在")
    
    return crud.create_comment(db=db, comment=comment, post_id=post_id, author_id=current_user.id)


@router.put("/comments/{comment_id}", response_model=Comment)
def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_comment = crud.update_comment(db=db, comment_id=comment_id, comment=comment, author_id=current_user.id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="评论不存在或无权修改")
    return db_comment


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    success = crud.delete_comment(db=db, comment_id=comment_id, author_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="评论不存在或无权删除")
    return {"message": "评论删除成功"}


@router.post("/posts/{post_id}/like")
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_post = crud.get_post(db, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if db_post.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能点赞自己的文章"
        )
    
    existing_like = crud.get_like(db, post_id, current_user.id)
    if existing_like:
        crud.delete_like(db, post_id, current_user.id)
        return {"message": "取消点赞", "liked": False}
    else:
        crud.create_like(db, post_id, current_user.id)
        return {"message": "点赞成功", "liked": True}


@router.post("/posts/{post_id}/favorite")
def toggle_favorite(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_post = crud.get_post(db, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    existing_favorite = crud.get_favorite(db, post_id, current_user.id)
    if existing_favorite:
        crud.delete_favorite(db, post_id, current_user.id)
        return {"message": "取消收藏", "favorited": False}
    else:
        crud.create_favorite(db, post_id, current_user.id)
        return {"message": "收藏成功", "favorited": True}


@router.get("/favorites", response_model=list[Favorite])
def read_favorites(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return crud.get_favorites_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="只支持 JPG、PNG、GIF、WEBP 格式的图片"
        )
    
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "url": f"/uploads/{filename}",
        "filename": filename
    }
