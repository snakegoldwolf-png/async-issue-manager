#!/usr/bin/env python3
"""
Issue Manager API Server
实时读取 .issues/ 目录数据，提供 REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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


def load_index():
    """加载 index.json"""
    if not INDEX_FILE.exists():
        return {"issues": [], "next_id": 1}
    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))


@app.get("/")
def root():
    """健康检查"""
    return {"status": "ok", "service": "Issue Manager API", "timestamp": datetime.now().isoformat()}


@app.get("/api/issues")
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


@app.get("/api/issues/{issue_id}")
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


@app.get("/api/stats")
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


@app.get("/api/agents")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8787)
