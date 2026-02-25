# Cloudflare Pages 部署指南

## 方案概述

采用**静态部署 + 定期数据推送**方案：
- Cloudflare Pages 托管前端
- GitHub Actions 定期生成静态 JSON
- 前端直接读取静态数据（无需 API 服务）

## 部署步骤

### 1. 准备 GitHub 仓库

```bash
cd ~/.openclaw/shared/async-issue-manager

# 初始化 Git（如果还没有）
git init
git add .
git commit -m "Initial commit: Async Issue Manager"

# 推送到 GitHub
git remote add origin https://github.com/你的用户名/async-issue-manager.git
git branch -M main
git push -u origin main
```

### 2. 配置 Cloudflare Pages

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 进入 **Pages** 页面
3. 点击 **Create a project**
4. 选择 **Connect to Git**
5. 授权并选择你的 GitHub 仓库
6. 配置构建设置：
   - **Project name**: `async-issue-manager`
   - **Production branch**: `main`
   - **Build command**: `cd web-dashboard && python3 generate_static_data.py`
   - **Build output directory**: `web-dashboard`
   - **Root directory**: `/`（留空）

7. 点击 **Save and Deploy**

### 3. 配置 GitHub Actions（自动更新）

#### 3.1 获取 Cloudflare API Token

1. 进入 [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens)
2. 点击 **Create Token**
3. 使用模板 **Edit Cloudflare Workers**
4. 或自定义权限：
   - Account > Cloudflare Pages > Edit
5. 复制生成的 Token

#### 3.2 获取 Account ID

1. 在 Cloudflare Dashboard 右侧找到 **Account ID**
2. 复制该 ID

#### 3.3 配置 GitHub Secrets

1. 进入 GitHub 仓库 **Settings** > **Secrets and variables** > **Actions**
2. 添加以下 Secrets：
   - `CLOUDFLARE_API_TOKEN`: 你的 API Token
   - `CLOUDFLARE_ACCOUNT_ID`: 你的 Account ID

#### 3.4 启用 GitHub Actions

GitHub Actions 配置文件已创建在 `.github/workflows/deploy.yml`

功能：
- 每次推送到 `main` 分支时自动部署
- 每小时自动更新一次数据
- 支持手动触发

### 4. 本地数据更新脚本

创建定时任务，定期推送最新数据到 GitHub：

```bash
# 创建更新脚本
cat > ~/.openclaw/shared/async-issue-manager/update_and_push.sh << 'EOF'
#!/bin/bash
cd ~/.openclaw/shared/async-issue-manager

# 生成最新数据
cd web-dashboard
python3 generate_static_data.py

# 提交并推送
cd ..
git add web-dashboard/data/
git commit -m "Update issue data - $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
EOF

chmod +x ~/.openclaw/shared/async-issue-manager/update_and_push.sh
```

#### 配置 cron 定时任务（每小时更新）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每小时执行一次）
0 * * * * ~/.openclaw/shared/async-issue-manager/update_and_push.sh >> ~/.openclaw/shared/async-issue-manager/update.log 2>&1
```

或使用 launchd（macOS 推荐）：

```bash
# 创建 plist 文件
cat > ~/Library/LaunchAgents/com.async-issue-manager.update.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.async-issue-manager.update</string>
    <key>ProgramArguments</key>
    <array>
        <string>$HOME/.openclaw/shared/async-issue-manager/update_and_push.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.openclaw/shared/async-issue-manager/update.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.openclaw/shared/async-issue-manager/update.error.log</string>
</dict>
</plist>
EOF

# 加载定时任务
launchctl load ~/Library/LaunchAgents/com.async-issue-manager.update.plist
```

### 5. 访问看板

部署完成后，你的看板将可以通过以下 URL 访问：

```
https://async-issue-manager.pages.dev
```

或自定义域名（在 Cloudflare Pages 设置中配置）。

## 手动触发更新

### 方法 1：GitHub Actions 手动触发

1. 进入 GitHub 仓库 **Actions** 页面
2. 选择 **Deploy to Cloudflare Pages** workflow
3. 点击 **Run workflow**

### 方法 2：本地推送

```bash
cd ~/.openclaw/shared/async-issue-manager
./update_and_push.sh
```

## 数据更新流程

```
本地 Issue 变更
    ↓
generate_static_data.py 生成 JSON
    ↓
Git commit & push
    ↓
GitHub Actions 触发
    ↓
Cloudflare Pages 自动部署
    ↓
全球 CDN 更新
    ↓
手机/浏览器访问最新数据
```

## 优势

✅ **无需服务器** - 完全静态托管，零运维成本  
✅ **全球 CDN** - Cloudflare 全球加速，访问速度快  
✅ **自动更新** - GitHub Actions 定期更新，数据保持同步  
✅ **免费额度** - Cloudflare Pages 免费版足够使用  
✅ **HTTPS** - 自动配置 SSL 证书  
✅ **手机友好** - 响应式设计，随时随地访问  

## 故障排除

### 部署失败

1. 检查 GitHub Actions 日志
2. 确认 Python 脚本执行成功
3. 检查 Cloudflare API Token 权限

### 数据未更新

1. 检查 GitHub Actions 是否正常运行
2. 查看 `update.log` 日志
3. 手动执行 `update_and_push.sh` 测试

### 访问 404

1. 确认 Build output directory 设置为 `web-dashboard`
2. 检查 `index.html` 是否在正确位置
3. 重新部署项目

## 后续优化

### P1
- [ ] 自定义域名配置
- [ ] 数据压缩（gzip）
- [ ] 缓存策略优化

### P2
- [ ] Webhook 触发（Issue 变更时立即更新）
- [ ] 增量更新（只更新变更的数据）
- [ ] 数据版本管理

### P3
- [ ] 多环境部署（dev/staging/prod）
- [ ] 访问统计（Cloudflare Analytics）
- [ ] 性能监控
