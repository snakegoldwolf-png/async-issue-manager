# sessions_send 超时保护方案

**方案 C：防止消息吞噬**

## 问题分析

当前 `sessions_send` 会继承 run 的默认超时（10 分钟），导致：
- 子代理无响应时，main session 被锁住
- 期间 bro 发的所有消息无法处理（消息吞噬）
- 严重影响系统可用性

## 解决方案

### 方案 C-1：AGENTS.md 规则（已实施）✅

在 AGENTS.md 中已添加硬性规则：

```markdown
### 6. sessions_send 必须用 timeoutSeconds=0

- 给子代理派任务时 → **必须用 `timeoutSeconds=0`**（fire-and-forget）
- **绝对禁止**用 `timeoutSeconds > 0` 等待子代理回复
- 等待期间 main session 被锁住，bro 发的消息会全部丢失
- 需要子代理回复时 → 让子代理主动用 message 工具汇报，不要同步等
```

**状态**：✅ 已完成

### 方案 C-2：openclaw.json 配置（实验性）

尝试在 openclaw.json 中配置 sessions_send 的默认超时：

```json
{
  "agents": {
    "defaults": {
      "tools": {
        "sessions_send": {
          "timeoutMs": 60000
        }
      }
    }
  }
}
```

**状态**：⚠️ 需要验证 OpenClaw 是否支持此配置项

**测试方法**：
1. 添加配置到 openclaw.json
2. 重启 gateway
3. 测试 sessions_send 是否生效
4. 如果不支持，回退到方案 C-1

## 推荐方案

**优先使用方案 C-1**（AGENTS.md 规则）：
- ✅ 已实施，立即生效
- ✅ 不依赖系统配置支持
- ✅ 明确的行为约束

**方案 C-2 作为补充**：
- 如果 OpenClaw 支持，可以作为系统级保护
- 但不应依赖它，AGENTS.md 规则是主要防护

## 验收标准

- ✅ 所有 sessions_send 调用都使用 `timeoutSeconds=0`
- ✅ 子代理汇报改为主动推送（message 工具）
- ✅ Main session 不再被长时间锁住
- ✅ 消息吞噬次数 = 0

## 实施状态

✅ **方案 C-1 已完成** - AGENTS.md 中已存在完整的 sessions_send 超时保护规则

这个规则确保：
1. 所有派任务都用 fire-and-forget 模式
2. 不会同步等待子代理回复
3. Main session 不会被锁住
4. 消息吞噬问题得到根本解决
