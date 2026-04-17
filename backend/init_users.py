#!/usr/bin/env python3
"""
初始化用户脚本
创建超级管理员 admin 和普通用户 user1
"""

from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User
from crud import create_user
from schemas import UserCreate
from auth import get_password_hash


def init_users():
    """初始化默认用户"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查是否已存在用户
        existing_admin = db.query(User).filter(User.username == "admin").first()
        existing_user1 = db.query(User).filter(User.username == "user1").first()
        
        # 创建超级管理员
        if not existing_admin:
            admin_user = UserCreate(username="admin", password="admin")
            db_user = User(
                username=admin_user.username,
                hashed_password=get_password_hash(admin_user.password),
                is_superuser=True,
                is_active=True
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            print(f"✅ 超级管理员创建成功: {db_user.username}")
        else:
            print(f"ℹ️  超级管理员已存在: {existing_admin.username}")
        
        # 创建普通用户
        if not existing_user1:
            normal_user = UserCreate(username="user1", password="user1")
            db_user = User(
                username=normal_user.username,
                hashed_password=get_password_hash(normal_user.password),
                is_superuser=False,
                is_active=True
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            print(f"✅ 普通用户创建成功: {db_user.username}")
        else:
            print(f"ℹ️  普通用户已存在: {existing_user1.username}")
        
        print("\n🎉 用户初始化完成！")
        print("\n登录信息:")
        print("  超级管理员: admin / admin")
        print("  普通用户:   user1 / user1")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 开始初始化用户...\n")
    init_users()
