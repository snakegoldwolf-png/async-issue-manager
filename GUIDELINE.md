# Async Issue Manager - 详细使用指南

本指南详细说明如何使用 Async Issue Manager 系统进行任务管理和团队协作。

## 目录

- [角色与权限](#角色与权限)
- [Issue 生命周期](#issue-生命周期)
- [创建 Issue](#创建-issue)
- [分配任务](#分配任务)
- [更新进度](#更新进度)
- [提交交付物](#提交交付物)
- [关闭 Issue](#关闭-issue)
- [查询与监控](#查询与监控)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 角色与权限

### 授权用户（Creator）

**权限**：
- ✅ 创建 Issue
- ✅ 分配 Issue 给 Agent
- ✅ 关闭 Issue
- ✅ 查看所有 Issue 和进度
- ✅ 管理交付物

**授权用户列表**：
- `bro`
- `loryoncloud`
- `admin`

**设置用户身份**：
```bash
export OPENCLAW_USER=bro
```

### Agent（Executor）

**权限**：
- ✅ 更新任务进度
- ✅ 提交交付物
- ✅ 查看所有 Issue 和进度
- ❌ 不能创建 Issue
- ❌ 不能分配或关闭 Issue

**Agent 列表**：
- 所有非授权用户都被视为 Agent

---

## Issue 生命周期

```
┌─────────┐
│  open   │  ← 创建时的初始状态
└────┬────┘
     │
     ↓ 分配给 Agent (manager.py assign)
┌─────────────┐
│ in-progress │  ← Agent 开始工作
└──────┬──────┘
       │
       ↓ 完成并提交交付物 (deliverable.py add)
       ↓ 关闭 Issue (manager.py close)
┌─────────┐
│ closed  │  ← 任务完成
└─────────┘
```

**状态说明**：
- `open` - 待处理，等待分配
- `in-progress` - 进行中，Agent 正在工作
- `closed` - 已关闭，任务完成

**注意**：`sync_progress.py` 中的 `--status` 参数（in-progress/blocked/review）只是进度标记，不会改变 Issue 的主状态。

---

## 创建 Issue

### 基本用法

```bash
cd ~/.openclaw/shared/async-issue-manager/scripts

python3 manager.py create \
  --title "Issue 标题" \
  --body "详细描述" \
  --priority P2 \
  --labels feature enhancement
```

### 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--title` | ✅ | Issue 标题 | "实现用户登录功能" |
| `--body` | ❌ | 详细描述（默认为空） | "需要支持邮箱和手机号登录" |
| `--priority` | ❌ | 优先级 (P0-P3，默认 P2) | P1 |
| `--labels` | ❌ | 标签（空格分隔） | bug hotfix |

### 优先级选择指南

| 优先级 | 场景 | 响应时间 | 示例 |
|--------|------|----------|------|
| **P0** | 系统崩溃、安全漏洞、数据丢失 | 立即处理 | 生产环境宕机 |
| **P1** | 重要功能、严重 bug、用户阻塞 | 24 小时内 | 支付功能失败 |
| **P2** | 常规功能、优化、中等 bug | 1 周内 | 添加搜索功能 |
| **P3** | 文档、清理、探索性任务 | 有空时处理 | 更新 README |

### 标签使用建议

**功能类型**：
- `feature` - 新功能开发
- `bug` - Bug 修复
- `enhancement` - 功能增强
- `docs` - 文档相关
- `test` - 测试相关

**紧急程度**：
- `hotfix` - 紧急修复
- `critical` - 关键任务

**技术领域**：
- `frontend` - 前端
- `backend` - 后端
- `database` - 数据库
- `api` - API 相关
- `performance` - 性能优化

**工作类型**：
- `research` - 研究探索
- `refactor` - 重构
- `cleanup` - 代码清理
- `security` - 安全相关

### 创建示例

#### 示例 1：紧急 Bug 修复

```bash
python3 manager.py create \
  --title "修复用户无法登录的问题" \
  --body "从昨晚开始，iOS 用户反馈无法登录，错误代码 500。影响约 30% 用户。" \
  --priority P0 \
  --labels bug hotfix critical backend
```

#### 示例 2：新功能开发

```bash
python3 manager.py create \
  --title "实现用户头像上传功能" \
  --body "需求：用户可以上传头像，支持 JPG/PNG，最大 5MB，自动裁剪为 200x200。" \
  --priority P2 \
  --labels feature frontend backend
```

#### 示例 3：文档任务

```bash
python3 manager.py create \
  --title "编写 API 文档" \
  --body "为新的用户管理 API 编写完整文档，包括请求示例和错误码说明。" \
  --priority P3 \
  --labels docs
```

---

## 分配任务

### 手动分配

```bash
# 将 Issue #1 分配给 debugger
python3 manager.py assign 1 debugger

# 创建时直接分配
python3 manager.py create \
  --title "修复内存泄漏" \
  --body "..." \
  --assignee debugger
```

### 智能广播（推荐）

系统会根据 Issue 的标签和优先级，推荐最合适的 Agent：

```bash
# 查看所有 open Issues 的推荐分配
python3 broadcast.py

# JSON 格式输出（便于程序处理）
python3 broadcast.py --json
```

**广播输出示例**：

```
==================================================
📢 Issue Broadcast - 2 open issues
==================================================

Issue #1: 修复用户无法登录的问题
  Priority: P0
  Labels: bug, hotfix, critical, backend
  Status: open
  
  🎯 推荐 Agent:
    - debugger (匹配度: 95%)
    - backend-dev (匹配度: 80%)

Issue #2: 实现用户头像上传功能
  Priority: P2
  Labels: feature, frontend, backend
  Status: open
  
  🎯 推荐 Agent:
    - fullstack-dev (匹配度: 90%)
    - frontend-dev (匹配度: 75%)
```

### 分配策略

1. **紧急任务（P0/P1）**：立即分配给最合适的 Agent
2. **常规任务（P2）**：参考广播推荐，考虑 Agent 当前负载
3. **低优先级（P3）**：可以等待 Agent 主动认领

---

## 更新进度

### Agent 更新进度

```bash
cd ~/.openclaw/shared/async-issue-manager/scripts

python3 sync_progress.py update <issue_id> \
  --progress "进度描述" \
  --status <状态> \
  --agent <agent_name>
```

### 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `issue_id` | ✅ | Issue ID | 1 |
| `--progress` | ✅ | 进度描述 | "已完成 50%" |
| `--status` | ❌ | 更新状态 | in-progress |
| `--agent` | ✅ | Agent 名称 | debugger |

### 状态说明

进度更新不会改变 Issue 的主状态（open/in-progress/closed），只是记录工作进展。`--status` 参数用于标记当前工作状态：

- `in-progress` - 正在工作中（默认）
- `blocked` - 遇到阻塞，需要帮助
- `review` - 完成待审核

注意：这些状态只记录在进度日志中，不会改变 Issue 文件的状态字段。

### 更新示例

#### 示例 1：开始工作

```bash
python3 sync_progress.py update 1 \
  --progress "开始分析问题，已拉取最新代码" \
  --status in-progress \
  --agent debugger
```

#### 示例 2：进度更新

```bash
python3 sync_progress.py update 1 \
  --progress "已定位问题：iOS 13 兼容性导致，正在修复" \
  --agent debugger
```

#### 示例 3：遇到阻塞

```bash
python3 sync_progress.py update 1 \
  --progress "需要数据库权限才能继续，等待 DBA 审批" \
  --status blocked \
  --agent debugger
```

#### 示例 4：完成工作

```bash
python3 sync_progress.py update 1 \
  --progress "修复完成，已通过所有测试，准备提交交付物" \
  --agent debugger
```

### 更新频率建议

- **P0 任务**：每 30 分钟更新一次
- **P1 任务**：每 1-2 小时更新一次
- **P2/P3 任务**：每天至少更新一次
- **关键节点**：立即更新（如遇到阻塞、完成重要里程碑）

---

## 提交交付物

### 为什么需要交付物？

交付物是任务完成的证明，确保：
- ✅ 工作成果可追溯
- ✅ 代码和文档完整
- ✅ 便于验收和审查
- ✅ 知识沉淀和复用

### 添加交付物

```bash
cd ~/.openclaw/shared/async-issue-manager/scripts

# 添加单个文件
python3 deliverable.py add <issue_id> \
  --file /path/to/file \
  --description "文件描述"

# 添加整个目录
python3 deliverable.py add <issue_id> \
  --file /path/to/directory/ \
  --description "目录描述"
```

### 交付物类型

#### 1. 代码文件

```bash
python3 deliverable.py add 1 \
  --file ~/project/src/auth/login.py \
  --description "修复后的登录模块代码"
```

#### 2. 配置文件

```bash
python3 deliverable.py add 1 \
  --file ~/project/config/nginx.conf \
  --description "更新后的 Nginx 配置"
```

#### 3. 文档

```bash
python3 deliverable.py add 1 \
  --file ~/project/docs/API.md \
  --description "用户管理 API 文档"
```

#### 4. 测试结果

```bash
python3 deliverable.py add 1 \
  --file ~/project/test_results/ \
  --description "单元测试和集成测试报告"
```

#### 5. 截图和日志

```bash
python3 deliverable.py add 1 \
  --file ~/screenshots/before_after.png \
  --description "修复前后对比截图"
```

### 查看交付物

```bash
# 列出所有交付物
python3 deliverable.py list

# 列出某个 Issue 的交付物
python3 deliverable.py list --issue 1

# 检查 Issue 是否有交付物
python3 deliverable.py check 1
```

### 交付物最佳实践

1. **完整性**：包含所有相关文件（代码、配置、文档、测试）
2. **描述清晰**：说明文件用途和修改内容
3. **及时提交**：完成工作后立即提交，不要拖延
4. **组织有序**：相关文件放在同一目录下
5. **可独立验证**：确保他人可以根据交付物复现结果

---

## 关闭 Issue

### 前提条件

关闭 Issue 前必须：
1. ✅ 提交至少一个交付物
2. ✅ 填写解决方案说明
3. ✅ 确认所有验收标准已满足

### 正常关闭

```bash
python3 manager.py close <issue_id> \
  --resolution "解决方案说明"
```

**示例**：

```bash
python3 manager.py close 1 \
  --resolution "已修复 iOS 13 兼容性问题，更新了登录模块代码，通过所有单元测试和集成测试。"
```

### 强制关闭（不推荐）

如果确实无法提交交付物（如任务取消），可以强制关闭：

```bash
python3 manager.py close 1 \
  --resolution "任务取消，需求变更" \
  --no-check-deliverable
```

⚠️ **警告**：强制关闭会跳过交付物检查，应谨慎使用。

### 关闭后的操作

Issue 关闭后：
- 文件移动到 `.issues/closed/` 目录
- 状态更新为 `closed`
- 记录关闭时间和解决方案
- 交付物保留在 `.issues/deliverables/` 目录

---

## 查询与监控

### 查看 Issue 列表

```bash
# 查看所有 open Issues
python3 manager.py list --status open

# 查看进行中的 Issues
python3 manager.py list --status in-progress

# 查看已关闭的 Issues
python3 manager.py list --status closed

# 按标签过滤
python3 manager.py list --status open --labels bug

# 查看某个 Agent 的任务
python3 manager.py list --assignee debugger
```

### 查看 Issue 详情

```bash
python3 manager.py show 1
```

**输出示例**：

```
==================================================
Issue #1: 修复用户无法登录的问题
==================================================
Status: closed
Priority: P0
Labels: bug, hotfix, critical, backend
Assignee: debugger
Created: 2024-02-25 10:00:00
Updated: 2024-02-25 14:30:00
Closed: 2024-02-25 14:30:00

Description:
从昨晚开始，iOS 用户反馈无法登录，错误代码 500。影响约 30% 用户。

Resolution:
已修复 iOS 13 兼容性问题，更新了登录模块代码，通过所有单元测试和集成测试。

Deliverables:
  - login.py (修复后的登录模块代码)
  - test_results/ (单元测试和集成测试报告)
```

### 查看进度记录

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

### 查看统计信息

```bash
python3 manager.py stats
```

**输出示例**：

```
==================================================
Issue Statistics
==================================================
Total: 10
  - open: 3
  - in-progress: 2
  - closed: 5

By Priority:
  - P0: 1
  - P1: 3
  - P2: 4
  - P3: 2

By Agent:
  - debugger: 3 issues
  - frontend-dev: 2 issues
  - backend-dev: 2 issues
```

### 监控工具

```bash
# 检查系统健康状态
python3 monitor.py

# 检查文件系统一致性
python3 inspector.py
```

---

## 最佳实践

### 1. 创建 Issue 时

✅ **好的做法**：

```bash
python3 manager.py create \
  --title "修复用户无法登录的问题" \
  --body "
问题描述：
从昨晚 22:00 开始，iOS 用户反馈无法登录，错误代码 500。

影响范围：
约 30% 的 iOS 用户（约 5000 人）

复现步骤：
1. 打开 App
2. 输入邮箱和密码
3. 点击登录按钮
4. 出现错误提示

期望结果：
用户可以正常登录

验收标准：
1. iOS 用户可以正常登录
2. 错误率降低到 0.1% 以下
3. 通过所有单元测试和集成测试
" \
  --priority P0 \
  --labels bug hotfix critical backend
```

❌ **不好的做法**：

```bash
python3 manager.py create \
  --title "登录问题" \
  --body "修一下"
```

### 2. 更新进度时

✅ **好的做法**：

```bash
# 具体、可量化、有时间节点
python3 sync_progress.py update 1 \
  --progress "已完成问题定位（耗时 2 小时）：
  - 根因：iOS 13 的 WebView 不支持某个 API
  - 影响范围：iOS 13.0-13.2 版本
  - 解决方案：使用兼容性 polyfill
  - 预计修复时间：2 小时
  - 当前进度：50%
  " \
  --agent debugger
```

❌ **不好的做法**：

```bash
python3 sync_progress.py update 1 \
  --progress "在做了" \
  --agent debugger
```

### 3. 提交交付物时

✅ **好的做法**：

```bash
# 提交完整的交付物，包含代码、测试、文档
python3 deliverable.py add 1 \
  --file ~/project/src/auth/login.py \
  --description "修复后的登录模块代码（添加了 iOS 13 兼容性处理）"

python3 deliverable.py add 1 \
  --file ~/project/tests/test_login.py \
  --description "更新后的单元测试（新增 iOS 13 兼容性测试用例）"

python3 deliverable.py add 1 \
  --file ~/project/docs/fix_ios13_login.md \
  --description "修复文档（包含问题分析、解决方案、测试结果）"
```

❌ **不好的做法**：

```bash
# 只提交代码，没有测试和文档
python3 deliverable.py add 1 \
  --file ~/project/src/auth/login.py \
  --description "代码"
```

### 4. 关闭 Issue 时

✅ **好的做法**：

```bash
python3 manager.py close 1 \
  --resolution "
问题已修复：
1. 根因：iOS 13 的 WebView 不支持 Promise.allSettled API
2. 解决方案：使用 core-js polyfill 提供兼容性支持
3. 测试结果：
   - 单元测试：100% 通过（新增 5 个测试用例）
   - 集成测试：100% 通过
   - 手动测试：iOS 13.0-13.7 全部通过
4. 部署情况：已部署到生产环境，监控 24 小时无异常
5. 错误率：从 30% 降低到 0.05%
"
```

❌ **不好的做法**：

```bash
python3 manager.py close 1 \
  --resolution "修好了"
```

### 5. 团队协作

- **及时沟通**：遇到阻塞立即更新状态并通知相关人员
- **定期同步**：每天至少更新一次进度
- **知识共享**：在交付物中包含详细文档，便于他人学习
- **代码审查**：关闭 Issue 前进行代码审查
- **持续改进**：定期回顾 Issue 处理流程，优化效率

---

## 常见问题

### Q1: 权限不足，无法创建 Issue

**错误信息**：
```
❌ 权限不足: 用户 'xxx' 无权创建 Issue
```

**解决方案**：
```bash
# 设置正确的用户身份
export OPENCLAW_USER=bro

# 或者在命令前临时设置
OPENCLAW_USER=bro python3 manager.py create --title "..." --body "..."
```

### Q2: 无法关闭 Issue，提示没有交付物

**错误信息**：
```
❌ Issue #1 没有交付物，无法关闭
```

**解决方案**：
```bash
# 先提交交付物
python3 deliverable.py add 1 --file /path/to/deliverable --description "..."

# 然后关闭 Issue
python3 manager.py close 1 --resolution "..."
```

### Q3: 文件系统状态不一致

**症状**：
- `manager.py list` 显示的 Issue 数量与实际文件不符
- Issue 文件存在但索引中找不到

**解决方案**：
```bash
# 运行同步命令，重建索引
python3 manager.py sync
```

### Q4: 如何批量操作 Issue？

**示例：批量关闭已完成的 Issue**

```bash
# 1. 列出所有 in-progress 的 Issue
python3 manager.py list --status in-progress --json > issues.json

# 2. 使用脚本批量处理
for issue_id in $(jq -r '.[].id' issues.json); do
  python3 manager.py close $issue_id --resolution "批量关闭" --no-check-deliverable
done
```

### Q5: 如何迁移到新的工作区？

```bash
# 1. 复制整个 async-issue-manager 目录
cp -r ~/.openclaw/shared/async-issue-manager /new/path/

# 2. 设置新的工作区路径（可选）
export OPENCLAW_WORKSPACE=/new/path

# 3. 验证迁移
cd /new/path/async-issue-manager/scripts
python3 manager.py list
```

### Q6: 如何备份和恢复？

**备份**：
```bash
# 备份整个 .issues 目录
tar -czf issues-backup-$(date +%Y%m%d).tar.gz ~/.openclaw/shared/async-issue-manager/.issues/
```

**恢复**：
```bash
# 解压备份
tar -xzf issues-backup-20240225.tar.gz -C ~/.openclaw/shared/async-issue-manager/

# 同步索引
cd ~/.openclaw/shared/async-issue-manager/scripts
python3 manager.py sync
```

### Q7: 如何集成到 CI/CD？

**示例：在 GitHub Actions 中自动创建 Issue**

```yaml
name: Create Issue on Test Failure

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Tests
        id: test
        run: |
          pytest || echo "test_failed=true" >> $GITHUB_OUTPUT
      
      - name: Create Issue on Failure
        if: steps.test.outputs.test_failed == 'true'
        run: |
          export OPENCLAW_USER=bro
          cd ~/.openclaw/shared/async-issue-manager/scripts
          python3 manager.py create \
            --title "测试失败: ${{ github.sha }}" \
            --body "Commit: ${{ github.sha }}\nBranch: ${{ github.ref }}\nAuthor: ${{ github.actor }}" \
            --priority P1 \
            --labels bug ci
```

---

## 附录

### A. 命令速查表

| 命令 | 说明 |
|------|------|
| `manager.py create` | 创建 Issue |
| `manager.py list` | 列出 Issues |
| `manager.py show <id>` | 查看 Issue 详情 |
| `manager.py assign <id> <agent>` | 分配 Issue |
| `manager.py close <id>` | 关闭 Issue |
| `manager.py stats` | 查看统计信息 |
| `manager.py sync` | 同步文件系统 |
| `sync_progress.py update` | 更新进度 |
| `sync_progress.py view` | 查看进度 |
| `sync_progress.py summary` | 生成摘要 |
| `deliverable.py add` | 添加交付物 |
| `deliverable.py list` | 列出交付物 |
| `deliverable.py check` | 检查交付物 |
| `broadcast.py` | 智能广播 |
| `monitor.py` | 监控系统 |
| `inspector.py` | 检查一致性 |

### B. 文件结构说明

```
.issues/
├── index.json              # Issue 索引（ID、状态、路径映射）
├── progress.jsonl          # 进度日志（JSONL 格式，每行一条记录）
├── open/                   # open 状态的 Issue
│   └── issue-001.md
├── in-progress/            # in-progress 状态的 Issue
│   └── issue-002.md
├── closed/                 # closed 状态的 Issue
│   └── issue-003.md
└── deliverables/           # 交付物存储
    ├── index.json          # 交付物索引
    ├── issue-001/          # Issue #1 的交付物
    │   ├── login.py
    │   └── test_results/
    └── issue-002/          # Issue #2 的交付物
        └── api_docs.md
```

### C. Issue Markdown 格式

```markdown
---
id: 1
title: 修复用户无法登录的问题
status: closed
priority: P0
labels:
  - bug
  - hotfix
  - critical
  - backend
assignee: debugger
created: 2024-02-25T10:00:00Z
updated: 2024-02-25T14:30:00Z
closed: 2024-02-25T14:30:00Z
---

## Description

从昨晚开始，iOS 用户反馈无法登录，错误代码 500。影响约 30% 用户。

## Resolution

已修复 iOS 13 兼容性问题，更新了登录模块代码，通过所有单元测试和集成测试。
```

### D. 进度日志格式

```jsonl
{"timestamp":"2024-02-25T10:30:00Z","issue_id":1,"agent":"debugger","progress":"开始分析问题","status":"in-progress"}
{"timestamp":"2024-02-25T12:00:00Z","issue_id":1,"agent":"debugger","progress":"已定位问题：iOS 13 兼容性导致","status":"in-progress"}
{"timestamp":"2024-02-25T14:00:00Z","issue_id":1,"agent":"debugger","progress":"修复完成，已通过所有测试","status":"in-progress"}
```

---

## 联系与支持

如有问题或建议，请联系：
- **Email**: support@example.com
- **GitHub**: https://github.com/your-org/async-issue-manager

---

**最后更新**: 2024-02-25  
**版本**: 2.0.0
