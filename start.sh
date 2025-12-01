#!/bin/bash

# ============================================================
# Nexus AI 项目启动脚本
# 支持同时启动前后端服务，可自定义端口
# ============================================================

set -e

# 默认端口配置
BACKEND_PORT=${BACKEND_PORT:-8080}
FRONTEND_PORT=${FRONTEND_PORT:-3003}

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 日志目录
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "$LOG_DIR"

# PID 文件
BACKEND_PID_FILE="${LOG_DIR}/backend.pid"
FRONTEND_PID_FILE="${LOG_DIR}/frontend.pid"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "
Usage: $0 [command] [options]

Commands:
    start       启动前后端服务 (默认)
    stop        停止所有服务
    restart     重启所有服务
    status      查看服务状态
    backend     仅启动后端服务
    frontend    仅启动前端服务

Options:
    -b, --backend-port PORT     设置后端端口 (默认: 8000)
    -f, --frontend-port PORT    设置前端端口 (默认: 3000)
    -h, --help                  显示帮助信息

Examples:
    $0                          # 使用默认端口启动
    $0 start -b 8080 -f 3001    # 自定义端口启动
    $0 stop                     # 停止所有服务
    $0 status                   # 查看服务状态

Environment Variables:
    BACKEND_PORT                后端端口 (优先级低于命令行参数)
    FRONTEND_PORT               前端端口 (优先级低于命令行参数)
"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口可用
    fi
}

# 获取占用端口的进程信息
get_port_process() {
    local port=$1
    lsof -Pi :$port -sTCP:LISTEN 2>/dev/null | tail -n +2 | awk '{print $1 " (PID: " $2 ")"}'
}

# 检查并处理端口冲突
handle_port_conflict() {
    local port=$1
    local service=$2

    if check_port $port; then
        print_warning "端口 $port 已被占用!"
        print_info "占用进程: $(get_port_process $port)"
        read -p "是否终止占用进程并继续? (y/N): " choice
        case "$choice" in
            y|Y)
                local pids=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null)
                if [ -n "$pids" ]; then
                    echo "$pids" | xargs kill -9 2>/dev/null
                    sleep 1
                    print_success "已终止占用端口 $port 的进程"
                fi
                ;;
            *)
                print_error "请指定其他端口运行 $service"
                exit 1
                ;;
        esac
    fi
}

# 启动后端服务
start_backend() {
    print_info "启动后端服务 (端口: $BACKEND_PORT)..."

    handle_port_conflict $BACKEND_PORT "后端服务"

    cd "$PROJECT_ROOT"

    # 激活 conda 环境 (如果存在)
    if command -v conda &> /dev/null; then
        print_info "激活 conda 环境: nexus-ai"
        eval "$(conda shell.bash hook)"
        conda activate nexus-ai 2>/dev/null || print_warning "conda 环境 nexus-ai 不存在，使用当前环境"
    fi

    # 启动 uvicorn
    nohup uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload \
        > "$LOG_DIR/backend.log" 2>&1 &

    echo $! > "$BACKEND_PID_FILE"

    sleep 2

    if check_port $BACKEND_PORT; then
        print_success "后端服务启动成功"
        print_info "后端地址: http://localhost:$BACKEND_PORT"
        print_info "API 文档: http://localhost:$BACKEND_PORT/docs"
    else
        print_error "后端服务启动失败，请检查日志: $LOG_DIR/backend.log"
        return 1
    fi
}

# 启动前端服务
start_frontend() {
    print_info "启动前端服务 (端口: $FRONTEND_PORT)..."

    handle_port_conflict $FRONTEND_PORT "前端服务"

    cd "$PROJECT_ROOT/web"

    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        print_info "安装前端依赖..."
        npm install
    fi

    # 设置前端环境变量，指向后端 API
    export NEXT_PUBLIC_API_URL="http://localhost:$BACKEND_PORT"

    # 启动 Next.js
    nohup npm run dev -- -p $FRONTEND_PORT \
        > "$LOG_DIR/frontend.log" 2>&1 &

    echo $! > "$FRONTEND_PID_FILE"

    sleep 3

    if check_port $FRONTEND_PORT; then
        print_success "前端服务启动成功"
        print_info "前端地址: http://localhost:$FRONTEND_PORT"
    else
        print_error "前端服务启动失败，请检查日志: $LOG_DIR/frontend.log"
        return 1
    fi
}

# 停止服务
stop_service() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid 2>/dev/null
            sleep 1
            # 强制终止如果还在运行
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null
            fi
            print_success "$service_name 已停止 (PID: $pid)"
        else
            print_warning "$service_name 进程不存在"
        fi
        rm -f "$pid_file"
    else
        print_warning "$service_name PID 文件不存在"
    fi
}

# 停止所有服务
stop_all() {
    print_info "停止所有服务..."
    stop_service "$BACKEND_PID_FILE" "后端服务"
    stop_service "$FRONTEND_PID_FILE" "前端服务"

    # 额外清理可能残留的进程
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true

    print_success "所有服务已停止"
}

# 查看服务状态
show_status() {
    echo ""
    echo "====== Nexus AI 服务状态 ======"
    echo ""

    # 后端状态
    if [ -f "$BACKEND_PID_FILE" ]; then
        local backend_pid=$(cat "$BACKEND_PID_FILE")
        if ps -p $backend_pid > /dev/null 2>&1; then
            print_success "后端服务: 运行中 (PID: $backend_pid)"
            # 尝试获取实际运行端口
            local backend_port=$(lsof -Pan -p $backend_pid -i | grep LISTEN | awk -F: '{print $2}' | awk '{print $1}' | head -1)
            [ -n "$backend_port" ] && print_info "  端口: $backend_port"
        else
            print_error "后端服务: 已停止"
        fi
    else
        print_warning "后端服务: 未启动"
    fi

    # 前端状态
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local frontend_pid=$(cat "$FRONTEND_PID_FILE")
        if ps -p $frontend_pid > /dev/null 2>&1; then
            print_success "前端服务: 运行中 (PID: $frontend_pid)"
        else
            print_error "前端服务: 已停止"
        fi
    else
        print_warning "前端服务: 未启动"
    fi

    echo ""
    echo "日志文件位置: $LOG_DIR/"
    echo ""
}

# 启动所有服务
start_all() {
    echo ""
    echo "======================================"
    echo "       Nexus AI 项目启动脚本"
    echo "======================================"
    echo ""

    start_backend
    echo ""
    start_frontend

    echo ""
    echo "======================================"
    print_success "所有服务启动完成!"
    echo ""
    print_info "后端: http://localhost:$BACKEND_PORT"
    print_info "前端: http://localhost:$FRONTEND_PORT"
    print_info "日志: $LOG_DIR/"
    echo "======================================"
}

# 解析命令行参数
COMMAND="start"

while [[ $# -gt 0 ]]; do
    case $1 in
        start|stop|restart|status|backend|frontend)
            COMMAND=$1
            shift
            ;;
        -b|--backend-port)
            BACKEND_PORT="$2"
            shift 2
            ;;
        -f|--frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 验证端口号
validate_port() {
    local port=$1
    local name=$2
    if ! [[ "$port" =~ ^[0-9]+$ ]] || [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
        print_error "无效的 $name 端口号: $port"
        exit 1
    fi
}

validate_port $BACKEND_PORT "后端"
validate_port $FRONTEND_PORT "前端"

# 执行命令
case $COMMAND in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 2
        start_all
        ;;
    status)
        show_status
        ;;
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
esac
