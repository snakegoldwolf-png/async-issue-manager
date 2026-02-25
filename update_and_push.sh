#!/bin/bash
# 自动更新并推送 Issue 数据到 GitHub

set -e

cd ~/.openclaw/shared/async-issue-manager

echo "🔄 [$(date '+%Y-%m-%d %H:%M:%S')] 开始更新 Issue 数据..."

# 生成最新数据
cd web-dashboard
python3 generate_static_data.py

# 检查是否有变更
cd ..
if git diff --quiet web-dashboard/data/; then
    echo "✅ 数据无变更，跳过推送"
    exit 0
fi

# 提交并推送
echo "📤 提交变更..."
git add web-dashboard/data/
git commit -m "Update issue data - $(date '+%Y-%m-%d %H:%M:%S')"

echo "🚀 推送到 GitHub..."
git push origin main

echo "✅ 更新完成！"
