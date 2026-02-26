#!/bin/bash
# 监控 .issues 目录变化，自动触发前端刷新
# 使用 fswatch 监控文件变化

ISSUES_DIR="$HOME/.openclaw/shared/async-issue-manager/.issues"

echo "🔄 开始监控 Issue 目录变化..."
echo "📁 监控目录: $ISSUES_DIR"

# 检查 fswatch 是否安装
if ! command -v fswatch &> /dev/null; then
    echo "⚠️  fswatch 未安装，正在安装..."
    brew install fswatch
fi

# 监控文件变化
fswatch -o "$ISSUES_DIR" | while read num; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') 检测到变化，API 会自动返回最新数据"
done
