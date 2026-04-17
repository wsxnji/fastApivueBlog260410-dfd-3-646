# 个人博客系统

一个简单的个人博客系统，使用 FastAPI + Vue 3 + SQLite 构建。

## 项目结构

```
helloBlog/
├── backend/          # FastAPI 后端
│   ├── main.py      # 主应用入口
│   ├── models.py    # 数据库模型
│   ├── schemas.py   # Pydantic 模式
│   ├── crud.py      # 数据库操作
│   ├── routes.py    # API 路由
│   └── database.py  # 数据库配置
└── frontend/         # Vue 3 前端
    ├── src/
    │   ├── views/   # 页面组件
    │   ├── api/     # API 调用
    │   └── router/  # 路由配置
    └── ...
```

## 快速开始

### 1. 启动后端

```bash
cd backend
# 安装依赖
pip3 install -r requirements.txt
# 启动服务
python3 -m uvicorn main:app --reload --port 8000
```

后端服务将在 http://localhost:8000 运行
API 文档地址：http://localhost:8000/docs

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 运行

## 功能特性

- ✅ 文章列表展示
- ✅ 文章详情查看
- ✅ 创建新文章
- ✅ 编辑文章
- ✅ 删除文章
- ✅ 响应式设计

## 技术栈

**后端**
- FastAPI - 现代高性能 Web 框架
- SQLAlchemy - ORM 框架
- SQLite - 轻量级数据库
- Pydantic - 数据验证

**前端**
- Vue 3 - 渐进式 JavaScript 框架
- Vue Router - 官方路由管理器
- Axios - HTTP 客户端
- Vite - 下一代前端构建工具

## API 接口

- GET /api/posts - 获取文章列表
- GET /api/posts/{id} - 获取单篇文章
- POST /api/posts - 创建文章
- PUT /api/posts/{id} - 更新文章
- DELETE /api/posts/{id} - 删除文章
