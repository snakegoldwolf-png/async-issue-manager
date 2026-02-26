# OpenClaw 团队公共知识库 - Obsidian 集成方案

> **文档版本**: v1.0  
> **创建日期**: 2026-02-25  
> **负责人**: Filer  
> **状态**: 草稿

---

## 1. 方案概述

### 1.1 目标

建立统一的团队知识库，将所有 Agent 产出的内容自动同步到 Obsidian，实现：
- ✅ 知识沉淀和管理
- ✅ 双链笔记网络
- ✅ 本地化存储，数据安全
- ✅ 离线可用，查询快速
- ✅ 版本控制（Git）

### 1.2 核心技术栈

| 技术 | 用途 | 说明 |
|------|------|------|
| **Obsidian** | 知识库平台 | 本地 Markdown 笔记应用 |
| **obsidian-cli** | 命令行工具 | 维护 wikilinks 完整性 |
| **write 工具** | 文件读写 | OpenClaw 内置工具 |
| **obsidian skill** | Agent 手册 | 教 Agent 如何组织笔记 |

### 1.3 工作流

```
Agent 产出内容
    ↓
自动识别内容类型
    ↓
路由到对应目录
    ↓
写入 Obsidian Vault
    ↓
建立双链关系
    ↓
更新索引
```

---

## 2. 目录结构设计

### 2.1 完整目录树

```
OpenClaw-Vault/
├── 00-系统/
│   ├── README.md                    # Vault 使用说明
│   ├── 目录结构规范.md              # 本文档
│   ├── 命名规范.md                  # 文件命名规则
│   └── 模板/                        # 笔记模板
│       ├── 日记模板.md
│       ├── 任务模板.md
│       └── 知识模板.md
├── 01-Agent/
│   ├── Filer/                       # 各 Agent 的个人空间
│   │   ├── 学习日记/
│   │   ├── 工作记录/
│   │   └── 知识沉淀/
│   ├── Debugger/
│   ├── Webby/
│   └── ...
├── 02-记忆库/
│   ├── 情景记忆/                    # 事件记录
│   │   ├── 2026/
│   │   │   ├── 02-February/
│   │   │   │   ├── 2026-02-25.md
│   │   │   │   └── ...
│   ├── 语义记忆/                    # 知识沉淀
│   │   ├── 技术/
│   │   │   ├── 文档工程化/
│   │   │   ├── 知识管理/
│   │   │   └── ...
│   │   ├── 方法论/
│   │   └── 工具/
│   └── 强制规则/                    # 不可违背的规则
│       ├── 工作区边界.md
│       ├── 数据治理原则.md
│       └── 安全规范.md
├── 03-任务管理/
│   ├── 任务清单.md                  # 当前任务
│   ├── 任务归档/                    # 已完成任务
│   │   ├── 2026-02/
│   │   └── ...
│   └── Issue 追踪/                  # Async Issue Manager 同步
│       ├── open/
│       ├── in-progress/
│       └── closed/
├── 04-项目/
│   ├── OpenClaw 系统/
│   │   ├── 架构设计/
│   │   ├── 功能开发/
│   │   └── 问题修复/
│   └── 其他项目/
├── 05-团队协作/
│   ├── 会议记录/
│   │   ├── 每日站会/
│   │   └── 专题讨论/
│   ├── 决策记录/
│   └── 知识分享/
├── 06-资源库/
│   ├── 参考资料/
│   │   ├── 文章/
│   │   ├── 推文/
│   │   └── 文档/
│   ├── 代码片段/
│   └── 工具清单/
└── 07-归档/
    ├── 2025/
    └── 2024/
```

### 2.2 目录说明

#### 00-系统
- **用途**: 存放 Vault 的元信息和规范
- **权限**: 只读（Agent 不应修改）
- **内容**: 使用说明、规范文档、模板

#### 01-Agent
- **用途**: 各 Agent 的个人工作空间
- **权限**: 各 Agent 只能写入自己的目录
- **内容**: 学习日记、工作记录、知识沉淀

#### 02-记忆库
- **用途**: 团队共享的知识库（核心）
- **权限**: 所有 Agent 可读写
- **内容**: 
  - 情景记忆：事件、日志、对话
  - 语义记忆：知识、方法论、工具
  - 强制规则：不可违背的原则

#### 03-任务管理
- **用途**: 任务追踪和管理
- **权限**: 所有 Agent 可读写
- **内容**: 任务清单、归档、Issue 同步

#### 04-项目
- **用途**: 项目相关的所有内容
- **权限**: 所有 Agent 可读写
- **内容**: 架构设计、功能开发、问题修复

#### 05-团队协作
- **用途**: 团队沟通和协作记录
- **权限**: 所有 Agent 可读写
- **内容**: 会议记录、决策记录、知识分享

#### 06-资源库
- **用途**: 外部资源和工具
- **权限**: 所有 Agent 可读写
- **内容**: 参考资料、代码片段、工具清单

#### 07-归档
- **用途**: 过期内容归档
- **权限**: 只读
- **内容**: 按年份归档的历史内容

---

## 3. 命名规范

### 3.1 文件命名规则

#### 日期相关文件
```
格式: YYYY-MM-DD-描述.md
示例: 2026-02-25-Obsidian集成方案.md
```

#### 知识文档
```
格式: 主题-子主题.md
示例: 文档工程化-Docs-as-Code.md
```

#### 任务文件
```
格式: [状态]任务名称.md
示例: [进行中]Obsidian集成.md
```

#### Agent 日记
```
格式: YYYY-MM-DD.md
示例: 2026-02-25.md
```

### 3.2 命名原则

1. **使用中文**: 便于阅读和搜索
2. **描述性**: 文件名应说明内容
3. **避免特殊字符**: 只用中文、英文、数字、`-`
4. **日期格式**: 统一使用 `YYYY-MM-DD`
5. **状态标记**: 用 `[]` 标记状态

---

## 4. Frontmatter 元数据标准

### 4.1 通用字段

```yaml
---
title: 文档标题
created: 2026-02-25T11:45:00+08:00
updated: 2026-02-25T11:45:00+08:00
author: Filer
type: knowledge|task|diary|meeting|reference
status: draft|in-progress|completed|archived
tags:
  - 标签1
  - 标签2
---
```

### 4.2 字段说明

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `title` | ✅ | 文档标题 | "Obsidian 集成方案" |
| `created` | ✅ | 创建时间（ISO 8601） | "2026-02-25T11:45:00+08:00" |
| `updated` | ✅ | 更新时间（ISO 8601） | "2026-02-25T11:45:00+08:00" |
| `author` | ✅ | 作者（Agent 名称） | "Filer" |
| `type` | ✅ | 文档类型 | "knowledge" |
| `status` | ❌ | 状态（可选） | "draft" |
| `tags` | ❌ | 标签（可选） | ["文档工程化", "Obsidian"] |

### 4.3 文档类型

- `knowledge` - 知识文档
- `task` - 任务相关
- `diary` - 日记
- `meeting` - 会议记录
- `reference` - 参考资料
- `decision` - 决策记录
- `code` - 代码相关

---

## 5. Wikilinks 使用规范

### 5.1 基本语法

```markdown
[[文件名]]                    # 链接到文件
[[文件名|显示文本]]           # 自定义显示文本
[[文件名#标题]]               # 链接到文件的特定标题
[[#标题]]                     # 链接到当前文件的标题
```

### 5.2 使用原则

1. **优先使用 wikilinks**: 而非 Markdown 链接
2. **使用相对路径**: 不要包含目录路径
3. **建立双向链接**: 相关内容互相链接
4. **标记关系**: 用标签和链接建立知识网络

### 5.3 示例

```markdown
# Obsidian 集成方案

本方案参考了 [[文档工程化-Docs-as-Code]] 的理念。

相关任务：[[Issue-6-Obsidian集成]]

参考资料：
- [[sitin推文-Obsidian集成实践]]
- [[Roland第二代AI系统]]

相关 Agent：[[Filer]] [[Memo]]
```

---

## 6. 自动同步机制

### 6.1 同步触发方式

#### 方式 1: Agent 主动写入
```python
# Agent 完成工作后，主动写入 Obsidian
write_to_obsidian(
    content=content,
    path="02-记忆库/语义记忆/技术/文档工程化/Obsidian集成.md",
    metadata={
        "author": "Filer",
        "type": "knowledge",
        "tags": ["Obsidian", "集成"]
    }
)
```

#### 方式 2: 定时同步
```bash
# 每小时同步一次
0 * * * * /path/to/sync_to_obsidian.sh
```

#### 方式 3: 事件触发
```python
# Issue 关闭时自动同步
on_issue_closed(issue_id):
    sync_issue_to_obsidian(issue_id)
```

### 6.2 同步内容类型

| 内容类型 | 源位置 | 目标位置 | 同步频率 |
|---------|--------|---------|---------|
| Agent 日记 | `Diary.md` | `01-Agent/{name}/学习日记/` | 每日 |
| Issue | `.issues/` | `03-任务管理/Issue追踪/` | 实时 |
| 会议记录 | 对话历史 | `05-团队协作/会议记录/` | 每次会议后 |
| 知识文档 | `memory/` | `02-记忆库/语义记忆/` | 实时 |
| 代码片段 | 工作区 | `06-资源库/代码片段/` | 按需 |

---

## 7. obsidian-cli 集成

### 7.1 安装

```bash
# macOS
brew tap yakitrak/yakitrak
brew install yakitrak/yakitrak/obsidian-cli

# 设置默认 Vault
obsidian-cli set-default "OpenClaw-Vault"
```

### 7.2 基本用法

```bash
# 创建笔记
obsidian-cli create "笔记标题" --vault "OpenClaw-Vault"

# 打开笔记
obsidian-cli open "笔记标题"

# 搜索笔记
obsidian-cli search "关键词"

# 列出所有笔记
obsidian-cli list

# 检查 wikilinks
obsidian-cli check-links
```

### 7.3 在 Python 中使用

```python
import subprocess

def create_obsidian_note(title, content, vault="OpenClaw-Vault"):
    """创建 Obsidian 笔记"""
    # 写入文件
    file_path = f"/path/to/{vault}/{title}.md"
    with open(file_path, 'w') as f:
        f.write(content)
    
    # 使用 obsidian-cli 维护 wikilinks
    subprocess.run([
        "obsidian-cli", "check-links",
        "--vault", vault
    ])

def open_obsidian_note(title):
    """打开 Obsidian 笔记"""
    subprocess.run([
        "obsidian-cli", "open", title
    ])
```

---

## 8. Agent 产出路由规则

### 8.1 路由表

| Agent | 产出类型 | 目标目录 |
|-------|---------|---------|
| **Filer** | 学习日记 | `01-Agent/Filer/学习日记/` |
| **Filer** | 文档规范 | `02-记忆库/语义记忆/方法论/` |
| **Debugger** | Bug 分析 | `04-项目/OpenClaw系统/问题修复/` |
| **Webby** | 网页内容 | `06-资源库/参考资料/文章/` |
| **Memo** | 会议记录 | `05-团队协作/会议记录/` |
| **所有 Agent** | 任务更新 | `03-任务管理/Issue追踪/` |

### 8.2 路由逻辑

```python
def route_content(agent, content_type, content):
    """根据 Agent 和内容类型路由到对应目录"""
    
    routing_rules = {
        ("Filer", "diary"): "01-Agent/Filer/学习日记/",
        ("Filer", "knowledge"): "02-记忆库/语义记忆/方法论/",
        ("Debugger", "bug_analysis"): "04-项目/OpenClaw系统/问题修复/",
        ("Webby", "article"): "06-资源库/参考资料/文章/",
        ("Memo", "meeting"): "05-团队协作/会议记录/",
        ("*", "task"): "03-任务管理/Issue追踪/",
    }
    
    # 查找路由规则
    key = (agent, content_type)
    if key in routing_rules:
        target_dir = routing_rules[key]
    else:
        # 默认路由到 Agent 个人空间
        target_dir = f"01-Agent/{agent}/工作记录/"
    
    return target_dir
```

---

## 9. 使用示例

### 9.1 Filer 写学习日记

```python
# Filer 完成一天的学习后
diary_content = """
---
title: 2026-02-25 学习日记
created: 2026-02-25T20:00:00+08:00
updated: 2026-02-25T20:00:00+08:00
author: Filer
type: diary
tags:
  - 学习
  - Obsidian
  - 文档工程化
---

# 2026-02-25 学习日记

## 今日学习

完成了 [[Issue-6-Obsidian集成]] 的方案设计。

学习了 [[obsidian-cli]] 的使用方法。

参考了 [[sitin推文-Obsidian集成实践]]。

## 关键收获

- Obsidian 的 wikilinks 机制
- 知识库目录结构设计原则
- 自动同步机制实现

## 下一步

明天实现自动同步脚本。
"""

# 写入 Obsidian
write_to_obsidian(
    content=diary_content,
    path="01-Agent/Filer/学习日记/2026-02-25.md"
)
```

### 9.2 Debugger 记录 Bug 分析

```python
bug_analysis = """
---
title: Issue-123 登录失败问题分析
created: 2026-02-25T15:00:00+08:00
updated: 2026-02-25T15:00:00+08:00
author: Debugger
type: knowledge
status: completed
tags:
  - Bug分析
  - 登录
  - iOS
---

# Issue-123 登录失败问题分析

## 问题描述

iOS 用户无法登录，错误代码 500。

相关 Issue: [[Issue-123-登录失败]]

## 根因分析

iOS 13 的 WebView 不支持 `Promise.allSettled` API。

参考: [[JavaScript兼容性问题]]

## 解决方案

使用 core-js polyfill 提供兼容性支持。

代码: [[登录模块修复代码]]

## 测试结果

- 单元测试：100% 通过
- 集成测试：100% 通过
- 手动测试：iOS 13.0-13.7 全部通过

## 相关人员

- 发现者: [[Anna]]
- 修复者: [[Debugger]]
- 验收者: [[bro]]
"""

write_to_obsidian(
    content=bug_analysis,
    path="04-项目/OpenClaw系统/问题修复/Issue-123-登录失败分析.md"
)
```

### 9.3 Memo 记录会议

```python
meeting_notes = """
---
title: 2026-02-25 每日站会
created: 2026-02-25T08:05:00+08:00
updated: 2026-02-25T08:30:00+08:00
author: Memo
type: meeting
tags:
  - 站会
  - 团队协作
---

# 2026-02-25 每日站会

## 参会人员

- [[Filer]]
- [[Debugger]]
- [[Webby]]
- [[Memo]]
- 其他 Agent...

## 进度汇报

### Filer
- 昨日: 学习 Async Issue Manager
- 今日: 完成 [[Issue-6-Obsidian集成]] 方案设计
- 阻塞: 无

### Debugger
- 昨日: 修复 [[Issue-123-登录失败]]
- 今日: 继续优化性能
- 阻塞: 无

## 决策事项

1. 统一使用 Obsidian 作为团队知识库
2. 所有 Agent 必须遵守 [[目录结构规范]]
3. 每日学习内容必须记录到 Obsidian

## 行动项

- [ ] Filer 完成 Obsidian 集成实现 (2026-02-26)
- [ ] 所有 Agent 学习 [[Obsidian使用指南]] (本周内)
"""

write_to_obsidian(
    content=meeting_notes,
    path="05-团队协作/会议记录/每日站会/2026-02-25.md"
)
```

---

## 10. 最佳实践

### 10.1 写作规范

1. **使用 frontmatter**: 每个文件都要有元数据
2. **建立链接**: 相关内容用 wikilinks 连接
3. **添加标签**: 便于分类和搜索
4. **结构清晰**: 使用标题层级组织内容
5. **及时更新**: 修改内容后更新 `updated` 字段

### 10.2 组织原则

1. **按类型分类**: 而非按时间
2. **避免深层嵌套**: 最多 3-4 层
3. **定期归档**: 过期内容移到归档目录
4. **保持整洁**: 删除无用文件
5. **统一命名**: 遵守命名规范

### 10.3 协作规范

1. **尊重他人空间**: 不要随意修改其他 Agent 的文件
2. **共享知识**: 有价值的内容放到共享目录
3. **及时同步**: 完成工作后立即写入 Obsidian
4. **建立索引**: 重要内容在 README 中索引
5. **版本控制**: 使用 Git 管理 Vault

---

## 11. 实现计划

### 11.1 Phase 1: 基础设施（今天）

- [x] 设计目录结构
- [x] 定义命名规范
- [x] 编写方案文档
- [ ] 创建 Vault 目录
- [ ] 编写模板文件
- [ ] 配置 obsidian-cli

### 11.2 Phase 2: 自动同步（明天上午）

- [ ] 实现同步脚本
- [ ] 实现路由逻辑
- [ ] 测试同步功能
- [ ] 处理边界情况

### 11.3 Phase 3: 文档和培训（明天下午）

- [ ] 编写使用指南
- [ ] 创建示例笔记
- [ ] 培训 Agent 使用
- [ ] 收集反馈优化

---

## 12. 风险和挑战

### 12.1 潜在风险

1. **文件冲突**: 多个 Agent 同时写入同一文件
2. **目录混乱**: Agent 不遵守规范随意创建文件
3. **性能问题**: Vault 文件过多导致 Obsidian 变慢
4. **同步延迟**: 实时同步可能影响性能

### 12.2 应对措施

1. **文件锁机制**: 写入前检查文件是否被占用
2. **严格规范**: 在 AGENTS.md 中明确规定
3. **定期清理**: 归档过期内容
4. **批量同步**: 非紧急内容批量同步

---

## 13. 后续优化方向

### 13.1 短期（1 个月内）

- 实现全文搜索功能
- 添加自动标签功能
- 优化同步性能
- 完善使用文档

### 13.2 中期（3 个月内）

- 实现知识图谱可视化
- 添加智能推荐功能
- 集成 AI 辅助写作
- 建立知识评分机制

### 13.3 长期（6 个月内）

- 实现多 Vault 管理
- 添加权限控制系统
- 集成外部知识源
- 建立知识质量体系

---

## 14. 总结

本方案提供了完整的 Obsidian 集成解决方案，包括：

✅ **目录结构**: 清晰的 7 大类目录  
✅ **命名规范**: 统一的文件命名规则  
✅ **元数据标准**: 标准化的 frontmatter  
✅ **同步机制**: 自动化的内容同步  
✅ **使用规范**: 详细的最佳实践  

**下一步**: 立即开始实现！

---

**文档状态**: 初稿完成  
**下一步**: 创建 Vault 目录结构，实现同步脚本
