# async-issue-manager 更新日志

## 2026-02-25 重要更新

### 1. 公有化部署 ✅
- 已将 async-issue-manager 从 `~/.openclaw/workspace-dev/` 迁移到 `~/.openclaw/shared/`
- 所有脚本已更新，优先使用共享目录
- 所有 Agent 现在都可以访问统一的 Issue 系统

### 2. 权限控制 ✅
- 新增 `auth.py` 权限控制模块
- 只有授权用户（bro, loryoncloud, admin）可以创建 Issue
- Agent 只能通过 `sync_progress.py` 更新任务进度
- `manager.py create` 命令已添加 `@require_create_permission()` 装饰器

### 3. 交付物强制要求 ✅
- 新增 `deliverable.py` 交付物管理工具
- 关闭 Issue 时强制检查是否有交付物
- 交付物统一存放在 `.issues/deliverables/issue-XXX/` 目录
- 支持文件和目录的交付

## 使用说明

### 创建 Issue（仅授权用户）
```bash
cd ~/.openclaw/shared/async-issue-manager/scripts
python3 manager.py create --title "任务标题" --body "描述" --priority P1 --labels bug fix
```

### Agent 更新进度
```bash
cd ~/.openclaw/shared/async-issue-manager/scripts
python3 sync_progress.py update <issue_id> --progress "进度描述" --status in-progress
```

### 添加交付物
```bash
cd ~/.openclaw/shared/async-issue-manager/scripts
python3 deliverable.py add <issue_id> --file <path> --description "交付物说明"
```

### 检查交付物
```bash
cd ~/.openclaw/shared/async-issue-manager/scripts
python3 deliverable.py check <issue_id>
```

### 关闭 Issue（需要交付物）
```bash
cd ~/.openclaw/shared/async-issue-manager/scripts
python3 manager.py close <issue_id> --resolution "解决说明"
```

## 目录结构
```
~/.openclaw/shared/async-issue-manager/
├── .issues/
│   ├── open/              # 待处理
│   ├── in-progress/       # 进行中
│   ├── closed/            # 已完成
│   ├── deliverables/      # 交付物目录
│   │   ├── issue-001/
│   │   ├── issue-002/
│   │   └── index.json
│   ├── index.json         # Issue 索引
│   └── progress.jsonl     # 进度日志
├── scripts/
│   ├── auth.py            # 权限控制 ⭐ 新增
│   ├── deliverable.py     # 交付物管理 ⭐ 新增
│   ├── manager.py         # Issue 管理（已更新）
│   ├── sync_progress.py   # 进度同步（已更新）
│   ├── monitor.py         # 任务监控（已更新）
│   └── broadcast.py       # Issue 广播
└── README.md
```

## 权限说明

### 授权用户（可创建 Issue）
- bro
- loryoncloud
- admin

### Agent（只能更新进度）
- debugger
- analyst
- writer
- discovery
- 其他所有 Agent

## 注意事项

1. **创建权限**: Agent 尝试创建 Issue 会被拒绝，提示使用 `sync_progress.py`
2. **交付物要求**: 关闭 Issue 时必须有交付物，否则无法关闭
3. **共享目录**: 所有操作都在 `~/.openclaw/shared/async-issue-manager/` 进行
4. **环境变量**: 可设置 `OPENCLAW_USER` 来指定当前用户身份
