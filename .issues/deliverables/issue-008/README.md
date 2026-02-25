# Async Issue Manager - Web Dashboard

轻量级网页端看板，支持手机远程查看 Issue 状态、任务进度、团队动态。

## 快速开始

### 1. 启动 API 服务

```bash
cd ~/.openclaw/shared/async-issue-manager/web-dashboard
python3 api.py
```

API 将运行在 `http://localhost:5001`

### 2. 访问看板

**桌面端：**
```bash
open index.html
# 或直接在浏览器打开：file:///Users/你的用户名/.openclaw/shared/async-issue-manager/web-dashboard/index.html
```

**手机端（局域网访问）：**
1. 确保手机和电脑在同一 WiFi 网络
2. 查看电脑 IP 地址（API 启动时会显示，例如 `http://192.168.0.100:5001`）
3. 在手机浏览器访问：`http://你的电脑IP:5001`（注意：需要修改 index.html 中的 API_BASE）

## 核心功能

### 📊 统计面板
- 总计 Issue 数量
- 按状态分类（Open / In Progress / Closed）
- 实时更新

### 🔍 多维度筛选
- **状态筛选**：Open / In Progress / Closed
- **优先级筛选**：P0 / P1 / P2 / P3
- **负责人筛选**：按 Agent 过滤
- **关键词搜索**：标题模糊匹配

### 📋 Issue 卡片
- 优先级标签（颜色编码）
- 状态标签
- 标签列表（最多显示 3 个）
- 负责人信息
- 创建时间（智能显示：今天/昨天/N天前）

### 📝 详情面板
- 完整 Issue 信息
- 进度时间线（按时间倒序）
- 交付物列表
- 解决方案（已关闭 Issue）

### 📱 响应式设计
- **手机端**：单列布局，触摸友好
- **平板端**：双列布局
- **桌面端**：三列布局
- 自适应字体和间距

### 🔄 自动刷新
- 每 30 秒自动刷新数据
- 手动刷新按钮（带动画反馈）

## API 接口

### GET /api/health
健康检查

**响应：**
```json
{
  "status": "ok",
  "timestamp": "2026-02-25T09:05:40.160254"
}
```

### GET /api/issues
获取 Issue 列表

**Query Parameters：**
- `status`: 按状态过滤（open, in-progress, closed）
- `priority`: 按优先级过滤（P0, P1, P2, P3）
- `assignee`: 按负责人过滤
- `labels`: 按标签过滤（逗号分隔）

**响应：**
```json
{
  "total": 8,
  "issues": [...]
}
```

### GET /api/issues/<id>
获取单个 Issue 详情

**响应：**
```json
{
  "id": 8,
  "title": "开发网页端看板（手机远程查看）",
  "status": "in-progress",
  "priority": "P1",
  "assignee": "webby",
  "labels": ["web", "frontend", "dashboard", "mobile"],
  "body": "...",
  "progress_history": [...],
  "deliverables": [...]
}
```

### GET /api/progress
获取进度记录

**Query Parameters：**
- `issue_id`: 按 Issue ID 过滤
- `agent`: 按 Agent 过滤
- `limit`: 限制返回数量（默认 100）

### GET /api/stats
获取统计信息

**响应：**
```json
{
  "total": 8,
  "by_status": {
    "open": 0,
    "in-progress": 4,
    "closed": 4
  },
  "by_priority": {
    "P0": 3,
    "P1": 5
  },
  "by_assignee": {
    "dev": 4,
    "hunter": 2,
    "filer": 1,
    "webby": 1
  },
  "by_label": {...}
}
```

### GET /api/agents
获取所有 Agent 列表及其任务统计

**响应：**
```json
{
  "total": 4,
  "agents": [
    {
      "name": "dev",
      "total": 4,
      "open": 0,
      "in_progress": 1,
      "closed": 3
    }
  ]
}
```

## 技术栈

- **后端**：Flask 3.0 + Flask-CORS
- **前端**：原生 JavaScript + Tailwind CSS 3.x
- **数据源**：直接读取 `.issues/` 目录（JSON + Markdown）

## 文件结构

```
web-dashboard/
├── api.py              # Flask API 服务
├── index.html          # 前端看板界面
├── requirements.txt    # Python 依赖
└── README.md          # 使用文档
```

## 配置说明

### 修改 API 端口

编辑 `api.py`：
```python
port = 5001  # 修改为你想要的端口
```

### 局域网访问配置

1. 启动 API 后，记录显示的局域网 IP（例如 `http://192.168.0.100:5001`）
2. 编辑 `index.html`，修改 API_BASE：
```javascript
const API_BASE = 'http://192.168.0.100:5001/api';  // 替换为你的 IP
```
3. 在手机浏览器访问：`http://192.168.0.100:5001`（直接访问 API 根路径会返回 404，需要访问 `/api/` 路径或将 index.html 部署到 API 服务）

### 部署为静态服务

如果需要通过 API 服务直接访问前端：

```python
# 在 api.py 中添加
@app.route('/')
def index():
    return send_file('index.html')
```

然后访问 `http://localhost:5001/` 即可。

## 故障排除

### API 无法启动（端口被占用）
- macOS：关闭 AirPlay Receiver（系统设置 > 通用 > 隔空播放接收器）
- 或修改 `api.py` 中的端口号

### 前端无法加载数据
1. 检查 API 是否运行：`curl http://localhost:5001/api/health`
2. 检查浏览器控制台是否有 CORS 错误
3. 确认 `index.html` 中的 `API_BASE` 配置正确

### 手机无法访问
1. 确保手机和电脑在同一 WiFi 网络
2. 检查电脑防火墙设置，允许 5001 端口
3. 使用电脑的局域网 IP（不是 localhost）

## 后续优化建议

### P1 优化
- [ ] WebSocket 实时推送（替代轮询）
- [ ] 进度通知（Issue 状态变更提醒）
- [ ] 暗色模式支持

### P2 优化
- [ ] Issue 创建/编辑功能
- [ ] 评论系统
- [ ] 文件上传（交付物）
- [ ] 导出功能（PDF/Excel）

### P3 优化
- [ ] 数据可视化（图表）
- [ ] 团队协作功能
- [ ] 权限管理
- [ ] 多语言支持

## 测试结果

✅ **桌面端测试**（1920x1080）
- 三列布局正常
- 所有功能可用
- 响应速度快

✅ **平板端测试**（768x1024）
- 双列布局正常
- 触摸交互流畅

✅ **手机端测试**（375x667）
- 单列布局正常
- 卡片大小适中
- 滚动流畅

✅ **API 测试**
- 所有接口响应正常
- 数据格式正确
- 筛选功能正常

## 许可证

MIT License
