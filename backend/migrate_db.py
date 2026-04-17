import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'blog.db')

def migrate_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("开始数据库迁移...")
    
    # 1. 备份现有posts数据
    print("1. 备份现有posts数据...")
    cursor.execute("SELECT id, title, content, summary, created_at, updated_at, author_id, is_hidden, category, tags FROM posts")
    posts_data = cursor.fetchall()
    print(f"   找到 {len(posts_data)} 篇文章")
    
    # 2. 备份users数据
    print("2. 备份现有users数据...")
    cursor.execute("SELECT id, username, hashed_password, is_superuser, is_active, created_at FROM users")
    users_data = cursor.fetchall()
    print(f"   找到 {len(users_data)} 个用户")
    
    # 3. 创建分类表（如果不存在）
    print("3. 创建categories表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL,
            description VARCHAR(200),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 4. 创建标签表（如果不存在）
    print("4. 创建tags表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 5. 创建文章-标签关联表（如果不存在）
    print("5. 创建post_tags表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_tags (
            post_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (post_id, tag_id),
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
    """)
    
    # 6. 插入默认分类
    print("6. 插入默认分类...")
    default_categories = [
        ('技术', '技术相关文章'),
        ('生活', '生活随笔'),
        ('其它', '其它分类')
    ]
    for name, desc in default_categories:
        try:
            cursor.execute("INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)", (name, desc))
        except:
            pass
    
    # 7. 从旧数据中提取所有标签
    print("7. 提取并创建标签...")
    all_tags = set()
    for post in posts_data:
        tags_str = post[9]  # tags字段
        if tags_str:
            tags = [t.strip() for t in tags_str.split(',') if t.strip()]
            all_tags.update(tags)
    
    for tag in all_tags:
        try:
            cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
        except:
            pass
    
    conn.commit()
    
    # 8. 获取分类ID映射
    cursor.execute("SELECT id, name FROM categories")
    category_map = {name: id for id, name in cursor.fetchall()}
    
    # 9. 获取标签ID映射
    cursor.execute("SELECT id, name FROM tags")
    tag_map = {name: id for id, name in cursor.fetchall()}
    
    # 10. 重命名旧posts表
    print("8. 重命名旧posts表...")
    cursor.execute("DROP TABLE IF EXISTS posts_old")
    cursor.execute("ALTER TABLE posts RENAME TO posts_old")
    
    # 11. 创建新的posts表
    print("9. 创建新的posts表...")
    cursor.execute("""
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            summary VARCHAR(500),
            cover_image VARCHAR(500),
            category_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            author_id INTEGER,
            is_hidden BOOLEAN DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)
    
    # 12. 迁移posts数据
    print("10. 迁移posts数据...")
    for post in posts_data:
        post_id, title, content, summary, created_at, updated_at, author_id, is_hidden, category_name, tags_str = post
        
        # 获取分类ID
        category_id = category_map.get(category_name, category_map.get('其它'))
        
        # 插入文章
        cursor.execute("""
            INSERT INTO posts (id, title, content, summary, cover_image, category_id, created_at, updated_at, author_id, is_hidden)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (post_id, title, content, summary, None, category_id, created_at, updated_at, author_id, is_hidden))
        
        # 处理标签关联
        if tags_str:
            tags = [t.strip() for t in tags_str.split(',') if t.strip()]
            for tag in tags:
                tag_id = tag_map.get(tag)
                if tag_id:
                    cursor.execute("INSERT OR IGNORE INTO post_tags (post_id, tag_id) VALUES (?, ?)", (post_id, tag_id))
    
    # 13. 删除旧表
    print("11. 清理旧表...")
    cursor.execute("DROP TABLE posts_old")
    
    # 14. 创建其他新表
    print("12. 创建评论、点赞、收藏表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            post_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            parent_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (author_id) REFERENCES users(id),
            FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("\n✅ 数据库迁移完成！")
    print(f"   - 用户数: {len(users_data)}")
    print(f"   - 文章数: {len(posts_data)}")
    print(f"   - 分类数: {len(category_map)}")
    print(f"   - 标签数: {len(tag_map)}")

if __name__ == "__main__":
    migrate_database()
