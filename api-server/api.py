#!/usr/bin/env python3
"""
Issue Manager API Server
实时读取 .issues/ 目录数据，提供 REST API
同时提供前端页面

路由结构：
- / : 主页占位
- /issues : Issue 看板
- /issues/api/* : API 端点
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Issue Manager API", version="1.0.0")

# CORS 配置 - 允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Issue 数据目录
ISSUES_DIR = Path.home() / ".openclaw/shared/async-issue-manager/.issues"
INDEX_FILE = ISSUES_DIR / "index.json"
PROGRESS_FILE = ISSUES_DIR / "progress.jsonl"
DELIVERABLES_FILE = ISSUES_DIR / "deliverables/index.json"

# 前端页面目录
WEB_DIR = Path.home() / ".openclaw/shared/async-issue-manager/web-dashboard"


def load_index():
    """加载 index.json"""
    if not INDEX_FILE.exists():
        return {"issues": [], "next_id": 1}
    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))


# ========================================
# 主页路由
# ========================================

@app.get("/", response_class=HTMLResponse)
def root():
    """主页"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LoryonClaw</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', -apple-system, sans-serif; }
        body {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 2rem;
        }
        h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p { color: #94a3b8; margin-bottom: 2.5rem; font-size: 1.2rem; }
        .links { display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; }
        a {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            color: #e2e8f0;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            text-decoration: none;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.2s;
            font-size: 1rem;
            font-weight: 500;
        }
        a:hover {
            background: rgba(255,255,255,0.1);
            border-color: rgba(255,255,255,0.2);
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .emoji { font-size: 5rem; margin-bottom: 1.5rem; }
    </style>
</head>
<body>
    <div class="emoji">🦎</div>
    <h1>LoryonClaw</h1>
    <p>AI Agent Team Workspace</p>
    <div class="links">
        <a href="/dashboard">📊 Dashboard</a>
        <a href="/issues">📋 Issues</a>
    </div>
</body>
</html>
    """)


@app.get("/health")
def health():
    """健康检查 API"""
    return {"status": "ok", "service": "LoryonClaw", "timestamp": datetime.now().isoformat()}


# ========================================
# Issue 看板路由 (/issues)
# ========================================

@app.get("/issues", response_class=HTMLResponse)
def issues_dashboard():
    """Issue 看板页面"""
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        # 读取并修改 API 路径
        content = index_file.read_text(encoding="utf-8")
        # 将 /api/ 替换为 /issues/api/
        content = content.replace("'/api/", "'/issues/api/")
        content = content.replace('"/api/', '"/issues/api/')
        content = content.replace('`/api/', '`/issues/api/')
        content = content.replace('fetch("/api', 'fetch("/issues/api')
        content = content.replace("fetch('/api", "fetch('/issues/api")
        content = content.replace("fetch(`/api", "fetch(`/issues/api")
        return HTMLResponse(content=content)
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


@app.get("/issues/dashboard", response_class=HTMLResponse)
@app.get("/issues/dashboard/", response_class=HTMLResponse)
def issues_dashboard_page():
    """Issue Dashboard 页面（兼容旧路径）"""
    dashboard_file = WEB_DIR / "dashboard" / "index.html"
    if dashboard_file.exists():
        return HTMLResponse(content=dashboard_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


@app.get("/issues/dashboard/data.json")
def issues_dashboard_data():
    """Dashboard 数据（兼容旧路径）"""
    data_file = WEB_DIR / "dashboard" / "data.json"
    if data_file.exists():
        return JSONResponse(content=json.loads(data_file.read_text(encoding="utf-8")))
    return JSONResponse(content={"error": "Data not found"}, status_code=404)


# ========================================
# 独立 Dashboard 路由 (/dashboard)
# ========================================

@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/dashboard/", response_class=HTMLResponse)
def dashboard_main():
    """独立 Dashboard 页面 - loryonclaw.me/dashboard"""
    dashboard_file = WEB_DIR / "dashboard" / "index.html"
    if dashboard_file.exists():
        return HTMLResponse(content=dashboard_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


@app.get("/dashboard/data.json")
def dashboard_main_data():
    """Dashboard 数据"""
    data_file = WEB_DIR / "dashboard" / "data.json"
    if data_file.exists():
        return JSONResponse(content=json.loads(data_file.read_text(encoding="utf-8")))
    return JSONResponse(content={"error": "Data not found"}, status_code=404)


# ========================================
# API 路由 (/issues/api/*)
# ========================================

@app.get("/issues/api/issues")
def get_issues():
    """获取所有 Issue 列表"""
    data = load_index()
    issues = data.get("issues", [])
    # 按 ID 倒序排列（最新的在前）
    issues = sorted(issues, key=lambda x: x.get("id", 0), reverse=True)
    return {"issues": issues, "total": len(issues)}


def parse_markdown_content(content: str) -> dict:
    """解析 Markdown 文件，提取 frontmatter 和 body"""
    result = {"body": "", "progress_history": [], "deliverables": []}
    
    lines = content.split("\n")
    body_lines = []
    
    i = 0
    # 跳过 frontmatter
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1  # 跳过结束的 ---
    
    # 收集所有正文内容
    while i < len(lines):
        body_lines.append(lines[i])
        i += 1
    
    result["body"] = "\n".join(body_lines).strip()
    return result


def load_progress(issue_id: int) -> list:
    """从 progress.jsonl 加载指定 Issue 的进度记录"""
    progress_list = []
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        record = json.loads(line)
                        if record.get('issue_id') == issue_id:
                            progress_list.append(record)
                    except json.JSONDecodeError:
                        continue
    # 按时间倒序排列（最新的在前）
    progress_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return progress_list


def load_deliverables(issue_id: int) -> list:
    """从 deliverables/index.json 加载指定 Issue 的交付物"""
    deliverables_list = []
    if DELIVERABLES_FILE.exists():
        try:
            data = json.loads(DELIVERABLES_FILE.read_text(encoding='utf-8'))
            for item in data.get('deliverables', []):
                if item.get('issue_id') == issue_id:
                    deliverables_list.append(item)
        except json.JSONDecodeError:
            pass
    return deliverables_list


@app.get("/issues/api/issues/{issue_id}")
def get_issue(issue_id: int):
    """获取单个 Issue 详情"""
    data = load_index()
    for issue in data.get("issues", []):
        if issue.get("id") == issue_id:
            # 尝试读取 Markdown 文件内容
            file_path = issue.get("file", "")
            file_exists = False
            if file_path:
                full_path = ISSUES_DIR.parent / file_path
                if full_path.exists():
                    file_exists = True
                    content = full_path.read_text(encoding="utf-8")
                    issue["content"] = content
                    # 解析 Markdown 内容
                    parsed = parse_markdown_content(content)
                    issue["body"] = parsed["body"]
            
            # 如果文件不存在，使用 resolution 作为 body
            if not file_exists:
                resolution = issue.get("resolution", "")
                if resolution:
                    issue["body"] = f"## 解决方案\n\n{resolution}"
                else:
                    issue["body"] = f"## {issue.get('title', 'Issue')}\n\n状态: {issue.get('status', 'unknown')}\n优先级: {issue.get('priority', 'unknown')}\n负责人: {issue.get('assignee', 'unassigned')}"
            
            # 加载进度记录和交付物
            issue["progress_history"] = load_progress(issue_id)
            issue["deliverables"] = load_deliverables(issue_id)
            
            return issue
    raise HTTPException(status_code=404, detail=f"Issue #{issue_id} not found")


@app.get("/issues/api/stats")
def get_stats():
    """获取统计数据"""
    data = load_index()
    issues = data.get("issues", [])
    
    stats = {
        "total": len(issues),
        "by_status": {},
        "by_priority": {},
        "by_assignee": {},
    }
    
    for issue in issues:
        # 按状态统计
        status = issue.get("status", "unknown")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        # 按优先级统计
        priority = issue.get("priority", "unknown")
        stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
        
        # 按负责人统计
        assignee = issue.get("assignee", "unassigned")
        stats["by_assignee"][assignee] = stats["by_assignee"].get(assignee, 0) + 1
    
    return stats


@app.get("/issues/api/agents")
def get_agents():
    """获取所有负责人列表"""
    data = load_index()
    issues = data.get("issues", [])
    
    agents = {}
    for issue in issues:
        assignee = issue.get("assignee", "unassigned")
        if assignee not in agents:
            agents[assignee] = {"name": assignee, "issues": 0, "open": 0, "closed": 0}
        agents[assignee]["issues"] += 1
        if issue.get("status") == "closed":
            agents[assignee]["closed"] += 1
        else:
            agents[assignee]["open"] += 1
    
    return {"agents": list(agents.values())}


# ========================================
# Token/Usage Dashboard API
# ========================================

def load_session_transcripts():
    """从 agents 目录加载 session transcript 文件获取 usage 数据"""
    agents_dir = Path.home() / ".openclaw/agents"
    sessions = []
    
    if not agents_dir.exists():
        return sessions
    
    # 遍历所有 agent 目录
    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir():
            continue
        
        agent_name = agent_dir.name
        sessions_dir = agent_dir / "sessions"
        
        if not sessions_dir.exists():
            continue
        
        for jsonl_file in sessions_dir.glob("*.jsonl"):
            try:
                session_id = jsonl_file.stem
                total_input = 0
                total_output = 0
                total_cost = 0
                request_count = 0
                last_model = ""
                last_timestamp = None
                
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            record = json.loads(line)
                            # 检查 message 类型的记录
                            if record.get('type') == 'message':
                                msg = record.get('message', {})
                                if msg.get('role') == 'assistant' and 'usage' in msg:
                                    usage = msg['usage']
                                    total_input += usage.get('input', 0)
                                    total_output += usage.get('output', 0)
                                    if 'cost' in usage and isinstance(usage['cost'], dict):
                                        total_cost += usage['cost'].get('total', 0)
                                    request_count += 1
                                    last_model = msg.get('model', '')
                                    if 'timestamp' in record:
                                        last_timestamp = record['timestamp']
                        except json.JSONDecodeError:
                            continue
                
                if request_count > 0:
                    sessions.append({
                        "session_id": session_id,
                        "agent": agent_name,
                        "input_tokens": total_input,
                        "output_tokens": total_output,
                        "total_tokens": total_input + total_output,
                        "cost": total_cost,
                        "requests": request_count,
                        "model": last_model,
                        "last_activity": last_timestamp
                    })
            except Exception:
                continue
    
    # 按总 token 数排序
    sessions.sort(key=lambda x: x['total_tokens'], reverse=True)
    return sessions


@app.get("/issues/api/usage")
def get_usage():
    """获取 Token 使用统计"""
    sessions = load_session_transcripts()
    
    # 汇总统计
    total_input = sum(s['input_tokens'] for s in sessions)
    total_output = sum(s['output_tokens'] for s in sessions)
    total_requests = sum(s['requests'] for s in sessions)
    total_cost = sum(s['cost'] for s in sessions)
    
    # 按 agent 分组
    by_agent = {}
    for s in sessions:
        agent = s.get('agent', 'unknown')
        if agent not in by_agent:
            by_agent[agent] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "requests": 0,
                "cost": 0,
                "sessions": 0
            }
        by_agent[agent]["input_tokens"] += s['input_tokens']
        by_agent[agent]["output_tokens"] += s['output_tokens']
        by_agent[agent]["total_tokens"] += s['total_tokens']
        by_agent[agent]["requests"] += s['requests']
        by_agent[agent]["cost"] += s['cost']
        by_agent[agent]["sessions"] += 1
    
    # 转换为列表并排序
    agents_list = [{"name": k, **v} for k, v in by_agent.items()]
    agents_list.sort(key=lambda x: x['total_tokens'], reverse=True)
    
    # 加载 Like·AI 统计数据
    likeai_stats = load_likeai_stats()
    
    return {
        "summary": {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "total_requests": total_requests,
            "total_cost": total_cost,
            "session_count": len(sessions),
            "agent_count": len(by_agent)
        },
        "by_agent": agents_list,
        "sessions": sessions[:50],  # 返回前 50 个 session
        "likeai": likeai_stats  # Like·AI 统计数据
    }


# Like·AI 统计缓存文件
LIKEAI_CACHE_FILE = Path.home() / ".openclaw/shared/async-issue-manager/.cache/likeai_stats.json"


def load_likeai_stats():
    """加载 Like·AI 统计数据（从缓存文件）"""
    if LIKEAI_CACHE_FILE.exists():
        try:
            return json.loads(LIKEAI_CACHE_FILE.read_text(encoding='utf-8'))
        except:
            return None
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8787)
