# 任务追踪系统

这个目录用于追踪长时间运行的任务，实现任务完成后的主动回报机制。

## 目录结构

```
.tasks/
├── task-{timestamp}.json       # 运行中的任务
├── completed/                  # 已完成任务归档
│   └── task-{timestamp}.json
└── failed/                     # 失败任务归档
    └── task-{timestamp}.json
```

## 任务文件格式

```json
{
  "id": "task-1708675200",
  "title": "任务标题",
  "assignee": "agent-name",
  "startTime": 1708675200,
  "estimatedDuration": 1800,
  "status": "running",
  "issueId": "001"
}
```

## 状态说明

- `running` - 任务进行中
- `completed` - 任务完成
- `failed` - 任务失败
- `timeout` - 任务超时

## 使用方式

参考 AGENTS.md 中的「任务完成主动回报机制」章节。
