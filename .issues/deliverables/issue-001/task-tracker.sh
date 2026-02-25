#!/bin/bash
# 任务追踪工具 - 创建、更新、检查任务状态

TASKS_DIR="$HOME/.openclaw/workspace/.tasks"

# 创建任务
create_task() {
    local title="$1"
    local assignee="$2"
    local estimated_duration="${3:-1800}"  # 默认 30 分钟
    local issue_id="${4:-}"
    
    local timestamp=$(date +%s)
    local task_id="task-${timestamp}"
    local task_file="${TASKS_DIR}/${task_id}.json"
    
    cat > "$task_file" <<EOF
{
  "id": "${task_id}",
  "title": "${title}",
  "assignee": "${assignee}",
  "startTime": ${timestamp},
  "estimatedDuration": ${estimated_duration},
  "status": "running",
  "issueId": "${issue_id}"
}
EOF
    
    echo "$task_id"
}

# 更新任务状态
update_task() {
    local task_id="$1"
    local status="$2"
    local result="${3:-}"
    local error="${4:-}"
    
    local task_file="${TASKS_DIR}/${task_id}.json"
    
    if [ ! -f "$task_file" ]; then
        echo "❌ 任务文件不存在: $task_file" >&2
        return 1
    fi
    
    local end_time=$(date +%s)
    
    # 读取原始数据
    local original=$(cat "$task_file")
    
    # 更新状态
    local updated=$(echo "$original" | jq --arg status "$status" \
        --arg endTime "$end_time" \
        --arg result "$result" \
        --arg error "$error" \
        '. + {status: $status, endTime: ($endTime | tonumber), result: $result, error: $error}')
    
    echo "$updated" > "$task_file"
    
    # 归档
    if [ "$status" = "completed" ]; then
        mv "$task_file" "${TASKS_DIR}/completed/"
    elif [ "$status" = "failed" ] || [ "$status" = "timeout" ]; then
        mv "$task_file" "${TASKS_DIR}/failed/"
    fi
    
    echo "✅ 任务状态已更新: $status"
}

# 检查任务状态
check_task() {
    local task_id="$1"
    local task_file="${TASKS_DIR}/${task_id}.json"
    
    if [ ! -f "$task_file" ]; then
        # 检查归档目录
        if [ -f "${TASKS_DIR}/completed/${task_id}.json" ]; then
            task_file="${TASKS_DIR}/completed/${task_id}.json"
        elif [ -f "${TASKS_DIR}/failed/${task_id}.json" ]; then
            task_file="${TASKS_DIR}/failed/${task_id}.json"
        else
            echo "❌ 任务不存在: $task_id" >&2
            return 1
        fi
    fi
    
    cat "$task_file" | jq .
}

# 列出所有运行中的任务
list_running() {
    echo "📋 运行中的任务："
    for task_file in "${TASKS_DIR}"/task-*.json; do
        if [ -f "$task_file" ]; then
            local task_id=$(basename "$task_file" .json)
            local title=$(jq -r '.title' "$task_file")
            local assignee=$(jq -r '.assignee' "$task_file")
            local start_time=$(jq -r '.startTime' "$task_file")
            local now=$(date +%s)
            local elapsed=$((now - start_time))
            local elapsed_min=$((elapsed / 60))
            
            echo "  - $task_id: $title (${assignee}, ${elapsed_min}分钟)"
        fi
    done
}

# 检查超时任务
check_timeout() {
    local now=$(date +%s)
    
    for task_file in "${TASKS_DIR}"/task-*.json; do
        if [ -f "$task_file" ]; then
            local task_id=$(basename "$task_file" .json)
            local start_time=$(jq -r '.startTime' "$task_file")
            local estimated_duration=$(jq -r '.estimatedDuration' "$task_file")
            local timeout_threshold=$((estimated_duration * 2))
            local elapsed=$((now - start_time))
            
            if [ $elapsed -gt $timeout_threshold ]; then
                echo "⚠️ 任务超时: $task_id (已运行 $((elapsed / 60)) 分钟，预计 $((estimated_duration / 60)) 分钟)"
                update_task "$task_id" "timeout" "" "任务执行时间超过预期的 2 倍"
            fi
        fi
    done
}

# 主函数
case "${1:-}" in
    create)
        create_task "$2" "$3" "${4:-1800}" "${5:-}"
        ;;
    update)
        update_task "$2" "$3" "${4:-}" "${5:-}"
        ;;
    check)
        check_task "$2"
        ;;
    list)
        list_running
        ;;
    timeout)
        check_timeout
        ;;
    *)
        echo "用法: $0 {create|update|check|list|timeout} [参数...]"
        echo ""
        echo "命令："
        echo "  create <title> <assignee> [duration] [issue_id]  - 创建任务"
        echo "  update <task_id> <status> [result] [error]       - 更新任务状态"
        echo "  check <task_id>                                   - 检查任务状态"
        echo "  list                                              - 列出运行中的任务"
        echo "  timeout                                           - 检查超时任务"
        exit 1
        ;;
esac
