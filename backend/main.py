from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import router

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Blog API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Welcome to Personal Blog API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
