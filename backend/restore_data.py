#!/usr/bin/env python3
"""
恢复博客系统的分类和标签数据
"""
import sqlite3
from datetime import datetime

DB_PATH = "blog.db"

def restore_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("开始恢复数据...")
    
    # 1. 恢复分类数据
    categories = [
        (1, "前端", "前端开发相关文章，包括HTML、CSS、JavaScript、Vue、React等", datetime.now().isoformat()),
        (2, "后端", "后端开发相关文章，包括Java、Python、Node.js、数据库等", datetime.now().isoformat()),
        (3, "数据库", "数据库技术相关文章，包括MySQL、PostgreSQL、Redis、MongoDB等", datetime.now().isoformat()),
        (4, "DevOps", "运维和DevOps相关文章，包括Docker、Kubernetes、CI/CD等", datetime.now().isoformat()),
        (5, "人工智能", "AI和机器学习相关文章", datetime.now().isoformat()),
    ]
    
    print("\n1. 恢复分类数据...")
    cursor.execute("DELETE FROM categories")
    cursor.executemany(
        "INSERT INTO categories (id, name, description, created_at) VALUES (?, ?, ?, ?)",
        categories
    )
    print(f"   ✅ 已恢复 {len(categories)} 个分类")
    
    # 2. 恢复标签数据
    tags = [
        (1, "Docker", datetime.now().isoformat()),
        (2, "微服务", datetime.now().isoformat()),
        (3, "AI", datetime.now().isoformat()),
        (4, "云原生", datetime.now().isoformat()),
        (5, "前端框架", datetime.now().isoformat()),
        (6, "数据库", datetime.now().isoformat()),
        (7, "Java", datetime.now().isoformat()),
        (8, "Vue", datetime.now().isoformat()),
        (9, "React", datetime.now().isoformat()),
        (10, "Kubernetes", datetime.now().isoformat()),
    ]
    
    print("\n2. 恢复标签数据...")
    cursor.execute("DELETE FROM tags")
    cursor.executemany(
        "INSERT INTO tags (id, name, created_at) VALUES (?, ?, ?)",
        tags
    )
    print(f"   ✅ 已恢复 {len(tags)} 个标签")
    
    # 3. 更新文章的分类和标签
    print("\n3. 更新文章的分类和标签关联...")
    
    # 文章分类和标签映射 (使用分类名称而不是ID，因为posts表使用category字段)
    category_names = {1: "前端", 2: "后端", 3: "数据库", 4: "DevOps", 5: "人工智能"}
    post_mappings = {
        1: (4, "Docker,Kubernetes"),  # Docker容器技术 -> DevOps
        2: (4, "微服务,Kubernetes"),  # 微服务架构 -> DevOps
        3: (5, "AI"),                  # AI应用 -> 人工智能
        4: (4, "云原生,Docker,Kubernetes"),  # 云原生 -> DevOps
        5: (1, "前端框架,Vue,React"),  # 前端框架 -> 前端
        6: (3, "数据库"),              # 数据库 -> 数据库
        7: (1, "前端框架"),            # 前端框架 -> 前端
        8: (3, "数据库"),              # 数据库 -> 数据库
        9: (2, "Java"),                # Java测试 -> 后端
    }
    
    for post_id, (category_id, tags_str) in post_mappings.items():
        category_name = category_names[category_id]
        cursor.execute(
            "UPDATE posts SET category = ?, tags = ? WHERE id = ?",
            (category_name, tags_str, post_id)
        )
    
    print(f"   ✅ 已更新 {len(post_mappings)} 篇文章的分类和标签")
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print("\n✅ 数据恢复完成！")
    print("\n恢复的数据：")
    print(f"  - 分类: {len(categories)} 个")
    print(f"  - 标签: {len(tags)} 个")
    print(f"  - 更新了 {len(post_mappings)} 篇文章的分类和标签")

if __name__ == "__main__":
    restore_data()
