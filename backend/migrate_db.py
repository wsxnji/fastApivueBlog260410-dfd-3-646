#!/usr/bin/env python3
"""
数据库迁移脚本：添加缺少的列
"""
import sqlite3

DB_PATH = "blog.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("开始数据库迁移...")
    
    # 检查 posts 表的列
    cursor.execute("PRAGMA table_info(posts)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"当前 posts 表列: {columns}")
    
    # 添加 cover_image 列（如果不存在）
    if 'cover_image' not in columns:
        print("添加 cover_image 列...")
        cursor.execute("ALTER TABLE posts ADD COLUMN cover_image VARCHAR(500)")
        print("  ✅ cover_image 列添加成功")
    else:
        print("  cover_image 列已存在")
    
    # 添加 category_id 列（如果不存在）
    if 'category_id' not in columns:
        print("添加 category_id 列...")
        cursor.execute("ALTER TABLE posts ADD COLUMN category_id INTEGER")
        print("  ✅ category_id 列添加成功")
    else:
        print("  category_id 列已存在")
    
    # 检查 category 列是否存在，如果存在且有数据，迁移到 category_id
    if 'category' in columns and 'category_id' in columns:
        print("\n迁移分类数据...")
        # 获取所有分类
        cursor.execute("SELECT id, name FROM categories")
        categories = {name: id for id, name in cursor.fetchall()}
        print(f"  找到分类: {categories}")
        
        # 更新文章的 category_id
        cursor.execute("SELECT id, category FROM posts WHERE category IS NOT NULL")
        posts = cursor.fetchall()
        for post_id, cat_name in posts:
            if cat_name in categories:
                cursor.execute(
                    "UPDATE posts SET category_id = ? WHERE id = ?",
                    (categories[cat_name], post_id)
                )
                print(f"  更新文章 {post_id} 的分类为 {cat_name} (ID: {categories[cat_name]})")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 数据库迁移完成！")

if __name__ == "__main__":
    migrate()
