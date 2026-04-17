#!/bin/bash
# 个人博客系统 - Docker启动脚本
### 1. 构建镜像### 2. 运行容器
# cd environment
# docker build -t blog-system -f Dockerfile .
# docker run -d -p 8000:8000 -p 5173:5173 --name blog-container blog-system
# pkill -f "uvicorn|vite"



PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKERFILE_DIR="$PROJECT_DIR/../"
IMAGE_NAME="personal-blog"
CONTAINER_NAME="personal-blog-container"

echo "========================================="
echo "   个人博客系统 - Docker启动脚本"
echo "========================================="
echo ""

# 检查参数
if [ $# -eq 0 ]; then
    echo "使用方法: $0 [build|run|stop|clean]"
    echo ""
    echo "选项:"
    echo "  build    - 构建Docker镜像"
    echo "  run      - 运行Docker容器（默认）"
    echo "  stop     - 停止Docker容器"
    echo "  clean    - 清理Docker镜像和容器"
    echo ""
    MODE="run"
else
    MODE="$1"
fi

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker未安装，请先安装Docker"
        exit 1
    fi
}

# 构建Docker镜像
build_image() {
    check_docker
    echo "🚀 构建Docker镜像..."
    echo ""
    
    cd "$DOCKERFILE_DIR"
    
    echo "📦 构建镜像: $IMAGE_NAME"
    docker build -t "$IMAGE_NAME" .
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Docker镜像构建成功！"
        echo "   镜像名称: $IMAGE_NAME"
    else
        echo ""
        echo "❌ Docker镜像构建失败"
        exit 1
    fi
}

# 运行Docker容器
run_container() {
    check_docker
    echo "🚀 运行Docker容器..."
    echo ""
    
    # 检查镜像是否存在
    if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
        echo "⚠️  镜像不存在，正在构建..."
        echo ""
        build_image
        echo ""
    fi
    
    # 检查容器是否已在运行
    if docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo "⚠️  容器已在运行，停止现有容器..."
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        echo ""
    fi
    
    echo "🎯 启动容器: $CONTAINER_NAME"
    echo "   映射端口: 8000 (后端API), 5173 (前端界面)"
    echo ""
    
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p 8000:8000 \
        -p 5173:5173 \
        "$IMAGE_NAME"
    
    if [ $? -eq 0 ]; then
        echo "✅ Docker容器启动成功！"
        echo ""
        echo "🌐 服务地址:"
        echo "   后端API: http://localhost:8000"
        echo "   API文档: http://localhost:8000/docs"
        echo "   前端界面: http://localhost:5173"
        echo ""
        echo "📋 查看容器状态:"
        echo "   docker ps -a | grep $CONTAINER_NAME"
        echo ""
        echo "📋 查看容器日志:"
        echo "   docker logs -f $CONTAINER_NAME"
    else
        echo "❌ Docker容器启动失败"
        exit 1
    fi
}

# 停止Docker容器
stop_container() {
    check_docker
    echo "🛑 停止Docker容器..."
    echo ""
    
    if docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo "停止容器: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        echo "✅ 容器已停止并删除"
    else
        echo "⚠️  容器 $CONTAINER_NAME 未在运行"
    fi
}

# 清理Docker资源
clean_resources() {
    check_docker
    echo "🧹 清理Docker资源..."
    echo ""
    
    # 停止并删除容器
    if docker ps -a --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo "删除容器: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" 2>/dev/null
        docker rm "$CONTAINER_NAME" 2>/dev/null
        echo "✅ 容器已删除"
    fi
    
    # 删除镜像
    if docker image inspect "$IMAGE_NAME" &> /dev/null; then
        echo "删除镜像: $IMAGE_NAME"
        docker rmi "$IMAGE_NAME"
        echo "✅ 镜像已删除"
    else
        echo "⚠️  镜像 $IMAGE_NAME 不存在"
    fi
}

# 根据模式执行操作
case "$MODE" in
    build)
        build_image
        ;;
    run)
        run_container
        ;;
    stop)
        stop_container
        ;;
    clean)
        clean_resources
        ;;
    *)
        echo "❌ 无效参数: $MODE"
        echo "使用方法: $0 [build|run|stop|clean]"
        exit 1
        ;;
esac
