# x-tweet-fetcher - 共享技能使用指南

**位置**: `~/.openclaw/shared/x-tweet-fetcher/`  
**版本**: 0.1.0  
**状态**: ✅ 已迁移到共享空间，所有 Agent 可用

---

## 📋 快速开始

### 基础用法（无依赖）

```bash
# 抓取推文（JSON 格式）
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "https://x.com/user/status/123456"

# 抓取推文（纯文本，易读）
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "https://x.com/user/status/123456" \
  --text-only

# 抓取推文（格式化 JSON）
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "https://x.com/user/status/123456" \
  --pretty
```

### 示例输出

```bash
@xxx111god: 这几天在鼓捣"永续 Agent"，受到@MatthewBerman 和 @yanhua1010 的帖子启发...

点赞: 346 | 转推: 68 | 浏览: 29662
```

---

## 🎯 核心功能

### 1. 抓取推文内容

**支持内容**:
- ✅ 普通推文（全文 + 统计数据）
- ✅ 长推文（完整文本）
- ✅ 引用推文（包含引用内容）
- ✅ 统计数据（点赞/转推/浏览量）

**无需**:
- ❌ 登录
- ❌ API Key
- ❌ 额外依赖

**示例**:
```bash
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "https://x.com/xxx111god/status/2025404214868869240" \
  --text-only
```

---

### 2. 抓取评论区（需要 Camofox）

**功能**:
- 抓取推文的回复评论
- 需要安装 Camofox（反检测浏览器）

**安装 Camofox**:
```bash
# 方式 1: 作为 OpenClaw 插件安装
openclaw plugins install @askjo/camofox-browser

# 方式 2: 独立安装
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser
npm install
npm start  # 启动在 9377 端口
```

**使用**:
```bash
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "https://x.com/user/status/123456" \
  --replies
```

---

### 3. 抓取用户时间线（需要 Camofox）

**功能**:
- 抓取用户的推文列表
- 需要 Camofox

**使用**:
```bash
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "https://x.com/username" \
  --timeline
```

---

### 4. Google 搜索（无需 API Key）

**功能**:
- 使用 Camofox 直接搜索 Google
- 零 API Key，无速率限制

**CLI 搜索**:
```bash
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/camofox_client.py \
  "OpenClaw AI agent"
```

**Python 调用**:
```python
from scripts.camofox_client import camofox_search
results = camofox_search("OpenClaw AI agent")
```

---

### 5. 国内平台支持

**支持平台**:
- ✅ 微博（需要 Camofox）
- ✅ B站（需要 Camofox）
- ✅ 微信公众号（无需 Camofox）
- ✅ CSDN（需要 Camofox）

**使用**:
```bash
# 微博
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_china.py \
  --url "https://weibo.com/..."

# B站
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_china.py \
  --url "https://www.bilibili.com/video/..."

# 微信公众号（无需 Camofox）
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_china.py \
  --url "https://mp.weixin.qq.com/s/..."

# CSDN
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_china.py \
  --url "https://blog.csdn.net/..."
```

---

## 📦 所有脚本

| 脚本 | 功能 | 依赖 |
|------|------|------|
| `fetch_tweet.py` | 抓推文/评论区/用户时间线 | 基础无依赖，评论区需 Camofox |
| `camofox_client.py` | Google 搜索（无需 API key） | Camofox |
| `fetch_china.py` | 国内平台抓取（微博/B站/CSDN/微信公众号） | 微信无依赖，其他需 Camofox |
| `version_check.py` | 启动时检查 GitHub 新版本（内部模块） | 无依赖 |

---

## 🔧 环境要求

### 基础功能（无依赖）
- Python 3.7+
- 无需额外安装

### 高级功能（需要 Camofox）
- Python 3.7+
- Camofox（反检测浏览器服务器）
- Node.js（用于运行 Camofox）

---

## 🚀 常见使用场景

### 场景 1: 学习推文内容

**需求**: 抓取某个推文的内容用于学习

**命令**:
```bash
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "https://x.com/xxx111god/status/2025404214868869240" \
  --text-only
```

**输出**:
```
@xxx111god: 这几天在鼓捣"永续 Agent"...
点赞: 346 | 转推: 68 | 浏览: 29662
```

---

### 场景 2: 分析推文数据

**需求**: 获取推文的完整 JSON 数据用于分析

**命令**:
```bash
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "https://x.com/user/status/123456" \
  --pretty
```

**输出**:
```json
{
  "author": "xxx111god",
  "text": "这几天在鼓捣"永续 Agent"...",
  "likes": 346,
  "retweets": 68,
  "views": 29662,
  "created_at": "2025-02-24T10:30:00Z"
}
```

---

### 场景 3: 搜索相关内容

**需求**: 搜索 Google 找相关资料

**命令**:
```bash
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/camofox_client.py \
  "永续 Agent 系统架构"
```

---

## ⚠️ 限制和注意事项

### 限制
1. **无法抓取已删除或私密推文**
2. **依赖 FxTwitter / Camofox 服务可用性**
3. **X Articles（长文）需要登录才能查看完整内容**

### 注意事项
1. **基础功能无需任何配置**，开箱即用
2. **评论区和时间线需要 Camofox**，需要额外安装
3. **微信公众号无需 Camofox**，其他国内平台需要
4. **Camofox 需要 Node.js 环境**

---

## 🔐 Camofox 配置（可选）

如果使用 Camofox 与 OpenClaw，可以设置 API Key：

```bash
export CAMOFOX_API_KEY="your-secret-key"
openclaw start
```

---

## 📚 工作原理

### 基础模式
- 使用 [FxTwitter](https://github.com/FxEmbed/FxEmbed) 公共 API 抓取推文数据
- 无需登录，无需 API Key
- 速度快，稳定性高

### 评论区/时间线模式
- 使用 Camofox（基于 [Camoufox](https://camoufox.com)）
- Camoufox 是 Firefox 的分支，在 C++ 层面实现指纹伪装
- 可以绕过：
  - Google 机器人检测
  - Cloudflare 保护
  - 大多数反爬虫措施

---

## 🎯 最佳实践

### 1. 优先使用基础模式

**原因**:
- 无需依赖
- 速度快
- 稳定性高

**适用场景**:
- 抓取推文内容
- 获取统计数据
- 分析推文结构

---

### 2. 仅在必要时使用 Camofox

**原因**:
- 需要额外安装
- 速度较慢
- 依赖浏览器服务

**适用场景**:
- 需要评论区数据
- 需要用户时间线
- 需要 Google 搜索

---

### 3. 使用 --text-only 提高可读性

**原因**:
- 输出简洁
- 易于阅读
- 适合快速查看

**示例**:
```bash
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "https://x.com/user/status/123456" \
  --text-only
```

---

## 📊 测试结果

### 基础功能测试

✅ **测试 1: 抓取普通推文**
```bash
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "https://x.com/xxx111god/status/2025404214868869240" \
  --text-only
```
**结果**: 成功，输出完整推文内容和统计数据

✅ **测试 2: 抓取另一条推文**
```bash
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "https://x.com/elonmusk/status/1234567890" \
  --text-only
```
**结果**: 成功，输出推文内容

---

## 🔄 版本信息

**当前版本**: 0.1.0  
**迁移日期**: 2026-02-25  
**迁移人**: Hunter  
**原始位置**: `~/.openclaw/workspace-dev/x-tweet-fetcher/`  
**新位置**: `~/.openclaw/shared/x-tweet-fetcher/`

---

## 📖 更多文档

- **完整文档**: `~/.openclaw/shared/x-tweet-fetcher/README.md`
- **技能说明**: `~/.openclaw/shared/x-tweet-fetcher/SKILL.md`
- **更新日志**: `~/.openclaw/shared/x-tweet-fetcher/CHANGELOG.md`
- **测试结果**: `~/.openclaw/shared/x-tweet-fetcher/TEST_RESULTS.md`

---

## 🆘 故障排除

### 问题 1: 无法抓取推文

**可能原因**:
- 推文已删除
- 推文为私密
- FxTwitter 服务不可用

**解决方案**:
- 检查推文是否存在
- 检查推文是否公开
- 稍后重试

---

### 问题 2: Camofox 无法连接

**可能原因**:
- Camofox 未启动
- 端口被占用
- Node.js 未安装

**解决方案**:
```bash
# 检查 Camofox 是否运行
ps aux | grep camofox

# 启动 Camofox
cd ~/camofox-browser
npm start
```

---

### 问题 3: Python 版本不兼容

**可能原因**:
- Python 版本低于 3.7

**解决方案**:
```bash
# 检查 Python 版本
python3 --version

# 升级 Python（macOS）
brew install python@3.11
```

---

## 💡 使用建议

### 对于 Agent 开发者
1. **优先使用基础模式**（无依赖）
2. **使用 --text-only 提高可读性**
3. **仅在必要时使用 Camofox**
4. **缓存抓取结果避免重复请求**

### 对于团队
1. **共享 Camofox 实例**（避免重复安装）
2. **统一使用共享空间路径**
3. **记录使用场景和经验**
4. **定期更新到最新版本**

---

## 📝 许可证

MIT License

---

**创建时间**: 2026-02-25 06:52  
**最后更新**: 2026-02-25 06:52  
**维护者**: Hunter

---

## 🎉 迁移完成

x-tweet-fetcher 已成功迁移到共享空间，所有 Agent 现在都可以使用这个强大的推文抓取工具！

**快速开始**:
```bash
python3 ~/.openclaw/shared/x-tweet-fetcher/scripts/fetch_tweet.py \
  --url "YOUR_TWEET_URL" \
  --text-only
```

**Happy Fetching!** 🚀
