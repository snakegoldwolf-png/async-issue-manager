# Issue #011 修复总结：子代理监控误报问题

**任务**: 修复 Leader 子代理进度监控 cron 的误判逻辑
**优先级**: P0
**实施时间**: 2026-02-25
**负责人**: 外部协助（Claude Code）

---

## 一、问题描述

Leader agent 的"子代理进度监控"cron job（ID: `ddf64bfe`）仅凭 `abortedLastRun` 标记和 `lastActivity` 时间戳判断子代理状态，导致大量误报。Gateway 日志证实 Dev 和 Debugger 都已完成任务并汇报，但 Leader 仍向 bro 发送"超时/无响应"警报。

### 根本原因

- `abortedLastRun=true` 只表示上一次 run 被超时中断，不代表 agent 没完成工作
- 旧 prompt 没有验证子代理的实际消息产出，直接根据表面指标下结论

---

## 二、修复内容

### 2.1 修改 cron job prompt（`~/.openclaw/cron/jobs.json`）

将原来的简单检查逻辑替换为四步验证流程：

1. **收集状态** — `sessions_list(activeMinutes=60, messageLimit=3)`
2. **验证实际产出** — 对疑似异常 session 调用 `sessions_history(limit=5)` 查看实际消息
3. **严格判断** — 必须同时满足三个条件才算"真正无响应"：aborted/超时 + 无产出 + 有待办任务
4. **分类处理** — 真正无响应才催促，已完成未转发则补转发，正常则静默

### 2.2 新增 AGENTS.md 防混乱规则第 7 条（`~/.openclaw/workspace/AGENTS.md`）

```
### 7. abortedLastRun ≠ agent 死亡

- abortedLastRun=true 只表示上一次 run 被超时中断
- agent 可能已经在超时前完成了工作并汇报了结果
- 判断 agent 是否完成任务，必须用 sessions_history 查看实际消息内容
- 绝对禁止仅凭 abortedLastRun=true 就向 bro 报告"agent 超时/无响应"
```

### 2.3 附带修复：路径错误（bonus）

修复了 4 个文件中 `workspace-dev/async-issue-manager` 的错误路径引用，统一改为 `shared/async-issue-manager`：

| 文件 | 修改处 |
|------|--------|
| `workspace/SOUL.md` | 系统位置 + cd 命令 |
| `workspace/MEMORY.md` | 系统位置 + cd 命令 |
| `knowledge/20-projects/async-issue-manager.md` | 代码仓库 + 配置文件路径 |
| `cron/jobs.json`（Memo 上下文监控） | 模板引用路径 |

---

## 三、修改文件清单

| 文件 | 改动类型 |
|------|----------|
| `~/.openclaw/cron/jobs.json` (job `ddf64bfe`) | 替换 cron prompt |
| `~/.openclaw/workspace/AGENTS.md` | 新增防混乱规则第 7 条 |
| `~/.openclaw/workspace/SOUL.md` | 路径修正 |
| `~/.openclaw/workspace/MEMORY.md` | 路径修正 |
| `~/.openclaw/knowledge/20-projects/async-issue-manager.md` | 路径修正 |
| `~/.openclaw/cron/jobs.json` (job `756373d9`) | Memo 模板路径修正 |

---

## 四、验证方式

1. 等下一次 cron 触发（每 10 分钟）
2. 观察 Gateway 日志，确认监控 cron 是否调用了 `sessions_history`
3. 观察飞书消息，确认是否还有未经验证的误报

### 初步验证结果

修改后首次 cron 执行耗时 10.5 秒（改前 27.8 秒），未产生误报通知，说明新逻辑正确跳过了已完成工作的 agent。

---

## 五、核心原则

> **abortedLastRun=true 不等于 agent 挂了。判断 agent 状态必须看 sessions_history 中的实际消息内容，不能只看表面指标。**
