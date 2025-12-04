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
CELERY_PID_FILE="${LOG_DIR}/celery.pid"

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
    start       启动所有服务 (后端 + 前端 + Celery)
    stop        停止所有服务
    restart     重启所有服务
    status      查看服务状态
    backend     仅启动后端服务
    frontend    仅启动前端服务
    celery      仅启动 Celery Worker
    celery-stop     停止 Celery Worker
    celery-restart  重启 Celery Worker

Options:
    -b, --backend-port PORT     设置后端端口 (默认: 8000)
    -f, --frontend-port PORT    设置前端端口 (默认: 3000)
    -h, --help                  显示帮助信息

Examples:
    $0                          # 使用默认端口启动所有服务
    $0 start -b 8080 -f 3001    # 自定义端口启动
    $0 stop                     # 停止所有服务
    $0 status                   # 查看服务状态
    $0 celery                   # 仅启动 Celery Worker
    $0 celery-restart           # 重启 Celery Worker

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

    # 等待后端启动（增加重试机制）
    print_info "等待后端服务启动..."
    local max_retries=10
    local retry=0
    while [ $retry -lt $max_retries ]; do
        sleep 1
        if check_port $BACKEND_PORT; then
            print_success "后端服务启动成功"
            print_info "后端地址: http://localhost:$BACKEND_PORT"
            print_info "API 文档: http://localhost:$BACKEND_PORT/docs"
            return 0
        fi
        # 检查日志中是否有 "Uvicorn running" 标志
        if grep -q "Uvicorn running\|Application startup complete" "$LOG_DIR/backend.log" 2>/dev/null; then
            print_success "后端服务启动成功"
            print_info "后端地址: http://localhost:$BACKEND_PORT"
            print_info "API 文档: http://localhost:$BACKEND_PORT/docs"
            return 0
        fi
        retry=$((retry + 1))
        print_info "等待中... ($retry/$max_retries)"
    done

    # 最终检查
    if grep -q "Uvicorn running\|Application startup complete" "$LOG_DIR/backend.log" 2>/dev/null; then
        print_success "后端服务启动成功 (通过日志确认)"
        print_info "后端地址: http://localhost:$BACKEND_PORT"
        print_info "API 文档: http://localhost:$BACKEND_PORT/docs"
        return 0
    fi

    print_error "后端服务启动失败，请检查日志: $LOG_DIR/backend.log"
    return 1
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

    # 等待前端启动（Next.js 启动较慢，增加重试机制）
    print_info "等待前端服务启动..."
    local max_retries=10
    local retry=0
    while [ $retry -lt $max_retries ]; do
        sleep 1
        if check_port $FRONTEND_PORT; then
            print_success "前端服务启动成功"
            print_info "前端地址: http://localhost:$FRONTEND_PORT"
            return 0
        fi
        # 检查日志中是否有 "Ready" 标志
        if grep -q "Ready in" "$LOG_DIR/frontend.log" 2>/dev/null; then
            print_success "前端服务启动成功"
            print_info "前端地址: http://localhost:$FRONTEND_PORT"
            return 0
        fi
        retry=$((retry + 1))
        print_info "等待中... ($retry/$max_retries)"
    done

    # 最终检查：即使端口检测失败，如果日志显示成功也算成功
    if grep -q "Ready in" "$LOG_DIR/frontend.log" 2>/dev/null; then
        print_success "前端服务启动成功 (通过日志确认)"
        print_info "前端地址: http://localhost:$FRONTEND_PORT"
        return 0
    fi

    print_error "前端服务启动失败，请检查日志: $LOG_DIR/frontend.log"
    return 1
}

# 启动 Celery Worker
start_celery() {
    print_info "启动 Celery Worker..."

    cd "$PROJECT_ROOT"

    # 激活 conda 环境 (如果存在)
    if command -v conda &> /dev/null; then
        print_info "激活 conda 环境: nexus-ai"
        eval "$(conda shell.bash hook)"
        conda activate nexus-ai 2>/dev/null || print_warning "conda 环境 nexus-ai 不存在，使用当前环境"
    fi

    # 检查是否已有 Celery 进程在运行
    if [ -f "$CELERY_PID_FILE" ]; then
        local old_pid=$(cat "$CELERY_PID_FILE")
        if ps -p $old_pid > /dev/null 2>&1; then
            print_warning "Celery Worker 已在运行 (PID: $old_pid)"
            return 0
        fi
    fi

    # 启动 Celery Worker
    # -A: 指定 Celery 应用
    # -l: 日志级别
    # -c: 并发数 (可根据需要调整)
    # --pidfile: PID 文件
    # --pool=solo: 单进程模式，避免 macOS fork 问题（Docling 等库不兼容 fork）
    # 注意：solo 模式下 --concurrency 无效，任务串行执行
    nohup celery -A app.tasks.celery_app worker \
        --loglevel=info \
        --pool=solo \
        --pidfile="$CELERY_PID_FILE" \
        > "$LOG_DIR/celery.log" 2>&1 &

    # 等待 Celery 启动
    print_info "等待 Celery Worker 启动..."
    local max_retries=10
    local retry=0
    while [ $retry -lt $max_retries ]; do
        sleep 1
        if [ -f "$CELERY_PID_FILE" ] && ps -p $(cat "$CELERY_PID_FILE" 2>/dev/null) > /dev/null 2>&1; then
            print_success "Celery Worker 启动成功 (PID: $(cat $CELERY_PID_FILE))"
            print_info "Celery 日志: $LOG_DIR/celery.log"
            return 0
        fi
        # 检查日志中是否有启动成功标志
        if grep -q "celery@.*ready\|Worker.*ready" "$LOG_DIR/celery.log" 2>/dev/null; then
            print_success "Celery Worker 启动成功"
            print_info "Celery 日志: $LOG_DIR/celery.log"
            return 0
        fi
        retry=$((retry + 1))
        print_info "等待中... ($retry/$max_retries)"
    done

    # 最终检查
    if grep -q "celery@.*ready\|Worker.*ready" "$LOG_DIR/celery.log" 2>/dev/null; then
        print_success "Celery Worker 启动成功 (通过日志确认)"
        return 0
    fi

    print_error "Celery Worker 启动失败，请检查日志: $LOG_DIR/celery.log"
    return 1
}

# 停止 Celery Worker
stop_celery() {
    print_info "停止 Celery Worker..."

    if [ -f "$CELERY_PID_FILE" ]; then
        local pid=$(cat "$CELERY_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            # 优雅关闭 Celery
            kill -TERM $pid 2>/dev/null
            sleep 2
            # 如果还在运行，强制终止
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null
            fi
            print_success "Celery Worker 已停止 (PID: $pid)"
        else
            print_warning "Celery Worker 进程不存在"
        fi
        rm -f "$CELERY_PID_FILE"
    else
        print_warning "Celery Worker PID 文件不存在"
    fi

    # 额外清理可能残留的 Celery 进程
    pkill -f "celery.*app.tasks.celery_app" 2>/dev/null || true
}

# 重启 Celery Worker
restart_celery() {
    stop_celery
    sleep 2
    start_celery
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
    stop_celery

    # 额外清理可能残留的进程
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    pkill -f "celery.*app.tasks.celery_app" 2>/dev/null || true

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

    # Celery Worker 状态
    if [ -f "$CELERY_PID_FILE" ]; then
        local celery_pid=$(cat "$CELERY_PID_FILE")
        if ps -p $celery_pid > /dev/null 2>&1; then
            print_success "Celery Worker: 运行中 (PID: $celery_pid)"
            # 显示 worker 并发数
            local concurrency=$(ps aux | grep "celery.*worker" | grep -v grep | wc -l)
            print_info "  Worker 进程数: $concurrency"
        else
            print_error "Celery Worker: 已停止"
        fi
    else
        print_warning "Celery Worker: 未启动"
    fi

    echo ""
    echo "日志文件位置:"
    echo "  后端日志: $LOG_DIR/backend.log"
    echo "  前端日志: $LOG_DIR/frontend.log"
    echo "  Celery 日志: $LOG_DIR/celery.log"
    echo "  模板任务日志: $LOG_DIR/template_tasks.log"
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
    start_celery

    echo ""
    echo "======================================"
    print_success "所有服务启动完成!"
    echo ""
    print_info "后端: http://localhost:$BACKEND_PORT"
    print_info "前端: http://localhost:$FRONTEND_PORT"
    print_info "Celery 日志: $LOG_DIR/celery.log"
    print_info "日志目录: $LOG_DIR/"
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
