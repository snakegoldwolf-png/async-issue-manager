# Async Issue Manager - Web Dashboard

轻量级 Issue 管理系统，支持本地 API 和 Cloudflare Pages 静态部署。

## 快速开始

### 本地开发模式

```bash
# 1. 启动 API 服务
cd ~/.openclaw/shared/async-issue-manager/web-dashboard
python3 api.py

# 2. 访问看板
open index.html
```

### 静态部署模式（Cloudflare Pages）

```bash
# 1. 生成静态数据
cd ~/.openclaw/shared/async-issue-manager/web-dashboard
python3 generate_static_data.py

# 2. 访问看板（自动使用静态数据）
open index.html
```

## 部署到 Cloudflare Pages

详细步骤请查看 [DEPLOY.md](./DEPLOY.md)

**快速摘要：**

1. 推送代码到 GitHub
2. 在 Cloudflare Pages 连接仓库
3. 配置构建：
   - Build command: `cd web-dashboard && python3 generate_static_data.py`
   - Build output: `web-dashboard`
4. 配置 GitHub Actions 自动更新（可选）
5. 访问：`https://your-project.pages.dev`

## 文件结构

```
web-dashboard/
├── api.py                      # Flask REST API（本地开发）
├── index.html                  # 响应式看板界面（支持静态/API 双模式）
├── generate_static_data.py     # 静态数据生成脚本
├── requirements.txt            # Python 依赖
├── data/                       # 静态数据目录（自动生成）
│   ├── issues.json            # 所有 Issue 列表
│   ├── stats.json             # 统计信息
│   ├── agents.json            # Agent 信息
│   ├── metadata.json          # 元数据
│   └── issues/                # 单个 Issue 详情
│       ├── 5.json
│       ├── 6.json
│       └── ...
├── DEPLOY.md                   # 部署指南
└── README.md                   # 本文件
```

## 功能特性

### 📊 统计面板
- 总计 Issue 数量
- 按状态分类（Open / In Progress / Closed）
- 实时更新

### 🔍 多维度筛选
- 状态筛选：Open / In Progress / Closed
- 优先级筛选：P0 / P1 / P2 / P3
- 负责人筛选：按 Agent 过滤
- 关键词搜索：标题模糊匹配

### 📋 Issue 卡片
- 优先级标签（颜色编码）
- 状态标签
- 标签列表（最多显示 3 个）
- 负责人信息
- 创建时间（智能显示）

### 📝 详情面板
- 完整 Issue 信息
- 进度时间线（按时间倒序）
- 交付物列表
- 解决方案（已关闭 Issue）

### 📱 响应式设计
- 手机端：单列布局
- 平板端：双列布局
- 桌面端：三列布局

### 🔄 数据模式

**API 模式**（本地开发）
- 实时读取 `.issues/` 目录
- 支持所有 REST API 接口
- 需要运行 `api.py`

**静态模式**（生产部署）
- 读取预生成的 JSON 文件
- 无需后端服务
- 适合 Cloudflare Pages 部署

切换模式：编辑 `index.html` 中的 `USE_STATIC_DATA` 变量

```javascript
const USE_STATIC_DATA = true;  // 静态模式
const USE_STATIC_DATA = false; // API 模式
```

## API 接口（本地模式）

### GET /api/health
健康检查

### GET /api/issues
获取 Issue 列表

**Query Parameters：**
- `status`: 按状态过滤
- `priority`: 按优先级过滤
- `assignee`: 按负责人过滤
- `labels`: 按标签过滤

### GET /api/issues/<id>
获取单个 Issue 详情

### GET /api/stats
获取统计信息

### GET /api/agents
获取 Agent 列表及统计

### GET /api/progress
获取进度记录

## 自动更新（Cloudflare Pages）

### GitHub Actions（推荐）

配置文件：`.github/workflows/deploy.yml`

- 每次推送自动部署
- 每小时自动更新数据
- 支持手动触发

### 本地定时任务

```bash
# 创建 cron 任务（每小时）
crontab -e

# 添加：
0 * * * * ~/.openclaw/shared/async-issue-manager/update_and_push.sh >> ~/.openclaw/shared/async-issue-manager/update.log 2>&1
```

或使用 launchd（macOS）：

```bash
# 加载定时任务
launchctl load ~/Library/LaunchAgents/com.async-issue-manager.update.plist
```

详细配置见 [DEPLOY.md](./DEPLOY.md)

## 技术栈

- **后端**：Flask 3.0 + Flask-CORS（本地模式）
- **前端**：原生 JavaScript + Tailwind CSS 3.x
- **部署**：Cloudflare Pages + GitHub Actions
- **数据源**：`.issues/` 目录（JSON + Markdown）

## 测试结果

✅ 桌面端（1920x1080）- 三列布局  
✅ 平板端（768x1024）- 双列布局  
✅ 手机端（375x667）- 单列布局  
✅ API 模式 - 所有接口正常  
✅ 静态模式 - 数据加载正常  

## 故障排除

### 本地 API 无法启动（端口被占用）
- macOS：关闭 AirPlay Receiver
- 或修改 `api.py` 中的端口号

### 静态数据未更新
```bash
cd ~/.openclaw/shared/async-issue-manager/web-dashboard
python3 generate_static_data.py
```

### Cloudflare Pages 部署失败
1. 检查 GitHub Actions 日志
2. 确认 Python 脚本执行成功
3. 检查 Cloudflare API Token 权限

详细故障排除见 [DEPLOY.md](./DEPLOY.md)

## 后续优化

### P1
- [ ] WebSocket 实时推送
- [ ] 暗色模式
- [ ] 自定义域名

### P2
- [ ] Issue 创建/编辑功能
- [ ] 评论系统
- [ ] 数据可视化（图表）

### P3
- [ ] 权限管理
- [ ] 多语言支持
- [ ] 离线支持（PWA）

## 许可证

MIT License
