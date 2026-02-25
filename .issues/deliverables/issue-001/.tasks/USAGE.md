# 任务主动回报机制 - 使用指南

## 概述

这套系统实现了 Agent 完成长时间任务后的主动回报功能，包括：
- 任务追踪（创建、更新、查询）
- 自动通知（完成/失败/超时）
- 简化的 API（task_helper.py）

## 快速开始

### 1. 开始一个任务

```bash
cd ~/.openclaw/workspace/scripts
python3 task_helper.py start "任务标题" "agent-name" --minutes 30 --issue "001"
```

**示例**：
```bash
python3 task_helper.py start "分析用户行为数据" "analyst" --minutes 60 --issue "015"
```

输出：
```
📋 任务已启动
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
任务 ID: task-1771972618
标题: 分析用户行为数据
负责人: analyst
预计耗时: 60 分钟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2. 完成任务

```bash
python3 task_helper.py complete task-1771972618 "分析完成，发现3个关键洞察"
```

系统会：
1. 更新任务状态为 `completed`
2. 归档任务文件到 `.tasks/completed/`
3. 自动发送飞书通知给 bro

### 3. 任务失败

```bash
python3 task_helper.py fail task-1771972618 "数据库连接超时"
```

系统会：
1. 更新任务状态为 `failed`
2. 归档任务文件到 `.tasks/failed/`
3. 自动发送失败通知

### 4. 查看任务状态

```bash
# 查看单个任务
python3 task_helper.py check task-1771972618

# 列出所有运行中的任务
python3 task_helper.py list
```

## 通知模板

### 完成通知

```
✅ 任务完成：分析用户行为数据

执行人：analyst
耗时：58 分钟
结果：分析完成，发现3个关键洞察

详情：任务 ID task-1771972618
关联 Issue: #015
```

### 失败通知

```
❌ 任务失败：分析用户行为数据

执行人：analyst
耗时：15 分钟
失败原因：数据库连接超时

详情：任务 ID task-1771972618
关联 Issue: #015
```

### 超时通知

```
⏰ 任务超时：分析用户行为数据

执行人：analyst
已运行：125 分钟
超时原因：任务执行时间超过预期的 2 倍 (125 分钟)

详情：任务 ID task-1771972618
关联 Issue: #015
```

## 在 Agent 中使用

### Python 代码示例

```python
import sys
from pathlib import Path

# 导入 task_helper
sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace" / "scripts"))
from task_helper import TaskHelper

# 创建助手实例
helper = TaskHelper()

# 开始任务
task_id = helper.start_task(
    title="处理用户反馈",
    assignee="support-agent",
    estimated_minutes=45,
    issue_id="023"
)

# ... 执行任务 ...

# 完成任务
helper.complete_task(task_id, "已处理 50 条反馈，创建了 3 个 Issue")

# 或者失败
# helper.fail_task(task_id, "API 限流，无法继续处理")
```

### Shell 脚本示例

```bash
#!/bin/bash

# 开始任务
TASK_ID=$(python3 ~/.openclaw/workspace/scripts/task_helper.py start \
    "备份数据库" "backup-agent" --minutes 30 | grep "任务 ID:" | awk '{print $3}')

echo "任务已启动: $TASK_ID"

# 执行任务
if pg_dump mydb > backup.sql; then
    # 成功
    python3 ~/.openclaw/workspace/scripts/task_helper.py complete \
        "$TASK_ID" "数据库备份成功，大小 2.3GB"
else
    # 失败
    python3 ~/.openclaw/workspace/scripts/task_helper.py fail \
        "$TASK_ID" "pg_dump 失败: $?"
fi
```

## 自动超时检查

可以设置 cron 任务定期检查超时：

```bash
# 每 10 分钟检查一次
*/10 * * * * cd ~/.openclaw/workspace/scripts && python3 task_tracker.py timeout
```

超时阈值：预计耗时的 2 倍

## 目录结构

```
~/.openclaw/workspace/
├── .tasks/
│   ├── README.md                    # 说明文档
│   ├── task-{timestamp}.json        # 运行中的任务
│   ├── completed/                   # 已完成任务归档
│   │   └── task-{timestamp}.json
│   └── failed/                      # 失败任务归档
│       └── task-{timestamp}.json
└── scripts/
    ├── task_tracker.py              # 核心追踪器
    ├── task_notifier.py             # 通知器
    ├── task_helper.py               # 简化 API
    └── task-tracker.sh              # Shell 版本（备用）
```

## 任务文件格式

```json
{
  "id": "task-1771972618",
  "title": "分析用户行为数据",
  "assignee": "analyst",
  "startTime": 1771972618,
  "estimatedDuration": 3600,
  "status": "completed",
  "issueId": "015",
  "endTime": 1771976118,
  "result": "分析完成，发现3个关键洞察"
}
```

## 高级用法

### 不发送通知

```bash
python3 task_helper.py complete task-1771972618 "完成" --no-notify
```

### 手动发送通知

```bash
python3 task_notifier.py --task-id task-1771972618
```

### 批量检查所有任务

```bash
python3 task_notifier.py --check-all
```

## 与 Issue Manager 集成

任务可以关联 Issue：

```bash
# 创建任务时关联 Issue
python3 task_helper.py start "修复登录 Bug" "debugger" --minutes 90 --issue "042"

# 完成后自动在通知中显示关联的 Issue
```

## 故障排查

### 问题：通知没有发送

**检查**：
1. 确认 `BRO_OPEN_ID` 正确（在 `task_notifier.py` 中）
2. 检查 OpenClaw message 工具是否可用
3. 查看日志：`python3 task_notifier.py --task-id <task_id>`

### 问题：任务文件找不到

**检查**：
1. 确认 `.tasks/` 目录存在
2. 检查任务 ID 是否正确
3. 查看归档目录：`ls ~/.openclaw/workspace/.tasks/{completed,failed}/`

### 问题：超时检查不工作

**检查**：
1. 确认 cron 任务已设置
2. 手动运行：`python3 task_tracker.py timeout`
3. 检查任务的 `estimatedDuration` 是否合理

## 最佳实践

1. **合理估算时间**：预计耗时应该接近实际，超时阈值是 2 倍
2. **及时更新状态**：完成或失败后立即更新，不要拖延
3. **详细的结果说明**：在 `result` 或 `error` 中提供足够的上下文
4. **关联 Issue**：如果任务来自 Issue，务必关联
5. **定期清理**：归档的任务可以定期清理（保留最近 30 天）

## 参考

- AGENTS.md - 任务完成主动回报机制章节
- Issue #017 - 原始需求
- @zohanlin 的实践：https://x.com/zohanlin/status/2024395335049892155

---

**最后更新**: 2026-02-25  
**版本**: 1.0.0
