# 🚀 Cloudflare Pages 部署快速指南

## 前置准备

- GitHub 账号
- Cloudflare 账号（免费版即可）
- Git 已配置

## 5 分钟快速部署

### Step 1: 推送到 GitHub

```bash
cd ~/.openclaw/shared/async-issue-manager

# 初始化 Git（如果还没有）
git init
git add .
git commit -m "Initial commit: Async Issue Manager"

# 创建 GitHub 仓库（在 GitHub 网站上创建）
# 然后推送
git remote add origin https://github.com/你的用户名/async-issue-manager.git
git branch -M main
git push -u origin main
```

### Step 2: 连接 Cloudflare Pages

1. 访问 https://dash.cloudflare.com/
2. 左侧菜单选择 **Workers & Pages**
3. 点击 **Create application** → **Pages** → **Connect to Git**
4. 授权 GitHub 并选择 `async-issue-manager` 仓库
5. 配置构建：

```
Project name: async-issue-manager
Production branch: main
Build command: cd web-dashboard && python3 generate_static_data.py
Build output directory: web-dashboard
```

6. 点击 **Save and Deploy**

### Step 3: 等待部署完成

- 首次部署约 1-2 分钟
- 完成后会显示 URL：`https://async-issue-manager.pages.dev`
- 点击访问即可看到看板

## 配置自动更新（可选）

### 方法 1: GitHub Actions（推荐）

#### 1. 获取 Cloudflare API Token

1. 访问 https://dash.cloudflare.com/profile/api-tokens
2. 点击 **Create Token**
3. 使用模板 **Edit Cloudflare Workers**
4. 复制生成的 Token

#### 2. 获取 Account ID

在 Cloudflare Dashboard 右侧找到 **Account ID** 并复制

#### 3. 配置 GitHub Secrets

1. 进入 GitHub 仓库 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加两个 Secrets：
   - Name: `CLOUDFLARE_API_TOKEN`, Value: 你的 API Token
   - Name: `CLOUDFLARE_ACCOUNT_ID`, Value: 你的 Account ID

#### 4. 启用 GitHub Actions

配置文件已创建在 `.github/workflows/deploy.yml`

功能：
- ✅ 每次推送自动部署
- ✅ 每小时自动更新数据
- ✅ 支持手动触发

### 方法 2: 本地定时推送

```bash
# 每次 Issue 变更后手动执行
cd ~/.openclaw/shared/async-issue-manager
./update_and_push.sh
```

或配置 cron 定时任务：

```bash
crontab -e

# 添加（每小时执行）
0 * * * * ~/.openclaw/shared/async-issue-manager/update_and_push.sh >> ~/.openclaw/shared/async-issue-manager/update.log 2>&1
```

## 访问看板

部署完成后，通过以下方式访问：

- **Cloudflare 默认域名**: `https://async-issue-manager.pages.dev`
- **手机访问**: 直接输入上述 URL
- **自定义域名**: 在 Cloudflare Pages 设置中配置

## 验证部署

1. 访问看板 URL
2. 检查统计面板是否显示正确数量
3. 点击任意 Issue 卡片查看详情
4. 测试筛选功能

## 常见问题

### Q: 部署失败怎么办？

A: 检查 Cloudflare Pages 部署日志：
1. 进入 Cloudflare Pages 项目
2. 点击 **View build log**
3. 查看错误信息

常见原因：
- Python 脚本执行失败 → 检查 `.issues/` 目录是否存在
- 路径配置错误 → 确认 Build output directory 为 `web-dashboard`

### Q: 数据没有更新？

A: 
1. 检查 GitHub Actions 是否正常运行（Actions 页面）
2. 手动触发更新：GitHub Actions → Run workflow
3. 或本地执行：`./update_and_push.sh`

### Q: 如何自定义域名？

A:
1. 进入 Cloudflare Pages 项目设置
2. 点击 **Custom domains**
3. 添加你的域名（需要在 Cloudflare 托管 DNS）

### Q: 免费版有限制吗？

A: Cloudflare Pages 免费版限制：
- ✅ 无限请求
- ✅ 无限带宽
- ✅ 500 次构建/月（足够使用）
- ✅ 1 次并发构建

## 数据更新流程

```
本地 Issue 变更
    ↓
generate_static_data.py 生成 JSON
    ↓
Git commit & push
    ↓
GitHub Actions 触发（或 Cloudflare 自动检测）
    ↓
Cloudflare Pages 重新构建
    ↓
全球 CDN 更新（约 1-2 分钟）
    ↓
手机/浏览器访问最新数据
```

## 优势总结

✅ **零成本** - Cloudflare Pages 免费版足够使用  
✅ **零运维** - 无需管理服务器  
✅ **全球加速** - Cloudflare CDN 覆盖全球  
✅ **自动 HTTPS** - 免费 SSL 证书  
✅ **自动更新** - GitHub Actions 定期同步  
✅ **随时访问** - 手机/电脑随时查看  

## 下一步

- [ ] 配置自定义域名
- [ ] 设置 GitHub Actions 自动更新
- [ ] 测试手机访问体验
- [ ] 分享给团队成员

## 需要帮助？

查看完整文档：[DEPLOY.md](./DEPLOY.md)
