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
    in_frontmatter = False
    body_lines = []
    current_section = None
    progress_entries = []
    
    i = 0
    # 跳过 frontmatter
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1  # 跳过结束的 ---
    
    # 解析正文
    while i < len(lines):
        line = lines[i]
        
        # 检测章节标题
        if line.startswith("## "):
            section_name = line[3:].strip().lower()
            if "进度" in section_name or "progress" in section_name:
                current_section = "progress"
            elif "交付" in section_name or "deliverable" in section_name:
                current_section = "deliverables"
            elif "描述" in section_name or "description" in section_name or "问题" in section_name:
                current_section = "body"
            else:
                current_section = "other"
                body_lines.append(line)
        elif current_section == "progress":
            # 解析进度记录 (格式: - [时间] agent: 内容)
            if line.strip().startswith("- "):
                progress_entries.append(line.strip()[2:])
        elif current_section == "deliverables":
            if line.strip().startswith("- "):
                result["deliverables"].append({
                    "file": line.strip()[2:],
                    "description": ""
                })
        else:
            body_lines.append(line)
        
        i += 1
    
    result["body"] = "\n".join(body_lines).strip()
    
    # 转换进度记录
    for entry in progress_entries:
        result["progress_history"].append({
            "timestamp": "",
            "agent": "",
            "progress": entry
        })
    
    return result


@app.get("/api/issues/{issue_id}")
def get_issue(issue_id: int):
    """获取单个 Issue 详情"""
    data = load_index()
    for issue in data.get("issues", []):
        if issue.get("id") == issue_id:
            # 尝试读取 Markdown 文件内容
            file_path = issue.get("file", "")
            if file_path:
                full_path = ISSUES_DIR.parent / file_path
                if full_path.exists():
                    content = full_path.read_text(encoding="utf-8")
                    issue["content"] = content
                    # 解析 Markdown 内容
                    parsed = parse_markdown_content(content)
                    issue["body"] = parsed["body"]
                    issue["progress_history"] = parsed["progress_history"]
                    issue["deliverables"] = parsed["deliverables"]
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
