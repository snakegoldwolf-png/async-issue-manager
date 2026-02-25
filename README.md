# Async Issue Manager

一个轻量级的本地 Issue 管理系统，专为 AI Agent 团队协作设计。支持权限控制、交付物管理、进度追踪和智能广播。

## 核心特性

- **权限控制** - 只有授权用户可以创建 Issue，Agent 只能更新进度
- **交付物管理** - 关闭 Issue 前必须提交交付物，确保任务质量
- **进度追踪** - 实时记录任务进度，支持多 Agent 协作
- **智能广播** - 根据标签和优先级自动匹配合适的 Agent
- **Git 友好** - 所有数据以 Markdown 和 JSON 存储，便于版本控制

## 快速开始

### 1. 创建 Issue（仅授权用户）

```bash
cd ~/.openclaw/shared/async-issue-manager/scripts

# 创建一个 P1 优先级的 bug 修复任务
python3 manager.py create \
  --title "修复登录页面崩溃问题" \
  --body "用户反馈在 iOS 设备上登录时应用崩溃" \
  --priority P1 \
  --labels bug hotfix
```

### 2. 查看 Issue 列表

```bash
# 查看所有 open 状态的 Issue
python3 manager.py list --status open

# 按标签过滤
python3 manager.py list --status open --labels bug

# 查看某个 Agent 的任务
python3 manager.py list --status in-progress --assignee debugger
```

### 3. 分配任务给 Agent

```bash
# 将 Issue #1 分配给 debugger
python3 manager.py assign 1 debugger
```

### 4. Agent 更新进度

```bash
# Agent 更新任务进度
python3 sync_progress.py update 1 \
  --progress "已定位问题：iOS 13 兼容性导致" \
  --status in-progress \
  --agent debugger
```

### 5. 提交交付物

```bash
# 添加修复后的代码文件
python3 deliverable.py add 1 \
  --file /path/to/fixed_code.py \
  --description "修复后的登录模块代码"

# 添加整个目录
python3 deliverable.py add 1 \
  --file /path/to/test_results/ \
  --description "测试报告和截图"
```

### 6. 关闭 Issue

```bash
# 关闭 Issue（需要先提交交付物）
python3 manager.py close 1 \
  --resolution "已修复 iOS 13 兼容性问题，通过所有测试"

# 强制关闭（不推荐）
python3 manager.py close 1 \
  --resolution "任务取消" \
  --no-check-deliverable
```

## 目录结构

```
async-issue-manager/
├── .issues/
│   ├── open/              # 待处理的 Issue
│   ├── in-progress/       # 进行中的 Issue
│   ├── closed/            # 已关闭的 Issue
│   ├── deliverables/      # 交付物存储
│   │   ├── issue-001/     # Issue #1 的交付物
│   │   ├── issue-002/     # Issue #2 的交付物
│   │   └── index.json     # 交付物索引
│   ├── index.json         # Issue 索引
│   └── progress.jsonl     # 进度日志
├── scripts/
│   ├── manager.py         # Issue 管理器
│   ├── auth.py            # 权限控制
│   ├── deliverable.py     # 交付物管理
│   ├── sync_progress.py   # 进度追踪
│   ├── broadcast.py       # 智能广播
│   ├── monitor.py         # 监控工具
│   └── inspector.py       # 检查工具
├── README.md              # 本文件
└── GUIDELINE.md           # 详细使用指南
```

## 权限说明

### 授权用户（可以创建 Issue）
- `bro`
- `loryoncloud`
- `admin`

### Agent（只能更新进度）
- 所有 Agent 只能通过 `sync_progress.py` 更新任务进度
- 不能创建、分配或关闭 Issue
- 可以查看所有 Issue 和进度

## 工作流程

```
1. 授权用户创建 Issue
   ↓
2. 系统广播给匹配的 Agent（可选）
   ↓
3. 授权用户分配 Issue 给 Agent
   ↓
4. Agent 更新进度（可多次）
   ↓
5. Agent 提交交付物
   ↓
6. 授权用户验收并关闭 Issue
```

## 常用命令

### Issue 管理

```bash
# 查看统计
python3 manager.py stats

# 查看 Issue 详情
python3 manager.py show 1

# 同步文件系统状态
python3 manager.py sync
```

### 进度追踪

```bash
# 查看所有进度记录
python3 sync_progress.py view

# 查看某个 Issue 的进度
python3 sync_progress.py view --issue 1

# 查看某个 Agent 的进度
python3 sync_progress.py view --agent debugger

# 生成进度摘要
python3 sync_progress.py summary
```

### 交付物管理

```bash
# 列出所有交付物
python3 deliverable.py list

# 列出某个 Issue 的交付物
python3 deliverable.py list --issue 1

# 检查 Issue 是否有交付物
python3 deliverable.py check 1
```

### 智能广播

```bash
# 广播所有 open Issues
python3 broadcast.py

# JSON 格式输出
python3 broadcast.py --json
```

## 优先级说明

- **P0** - 紧急（系统崩溃、安全漏洞）
- **P1** - 高优先级（重要功能、严重 bug）
- **P2** - 中优先级（常规功能、优化）
- **P3** - 低优先级（文档、清理、探索）

## 标签示例

- `bug` - Bug 修复
- `feature` - 新功能
- `docs` - 文档
- `performance` - 性能优化
- `hotfix` - 紧急修复
- `enhancement` - 功能增强
- `research` - 研究探索
- `cleanup` - 代码清理

## 环境变量

```bash
# 设置当前用户（用于权限检查）
export OPENCLAW_USER=bro

# 自定义工作区路径（可选）
export OPENCLAW_WORKSPACE=/path/to/workspace
```

## 最佳实践

1. **创建 Issue 时**
   - 标题简洁明确
   - 描述包含背景、目标、验收标准
   - 设置合适的优先级和标签

2. **分配任务时**
   - 根据 Agent 专长分配
   - 使用 `broadcast.py` 查看推荐匹配

3. **更新进度时**
   - 定期更新（建议每小时或关键节点）
   - 描述具体进展和遇到的问题
   - 遇到阻塞及时标记 `--status blocked`

4. **提交交付物时**
   - 包含所有相关文件（代码、文档、测试）
   - 添加清晰的描述说明
   - 确保交付物可独立验证

5. **关闭 Issue 时**
   - 验证交付物完整性
   - 填写详细的解决方案说明
   - 确认所有验收标准已满足

## 故障排查

### 权限错误

```bash
❌ 权限不足: 用户 'xxx' 无权创建 Issue
```

**解决方案**：设置正确的用户身份
```bash
export OPENCLAW_USER=bro
```

### 无法关闭 Issue

```bash
❌ Issue #1 没有交付物，无法关闭
```

**解决方案**：先提交交付物
```bash
python3 deliverable.py add 1 --file /path/to/deliverable
```

### 文件系统不同步

```bash
# 运行同步命令
python3 manager.py sync
```

## 更多信息

详细使用指南请参考 [GUIDELINE.md](./GUIDELINE.md)

## License

MIT
