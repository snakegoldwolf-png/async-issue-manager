#!/usr/bin/env python3
"""
Async Issue Manager - Web Dashboard API
轻量级 Flask API，读取 Issue 数据并提供 REST 接口
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置路径
BASE_DIR = Path(__file__).parent.parent
ISSUES_DIR = BASE_DIR / ".issues"
INDEX_FILE = ISSUES_DIR / "index.json"
PROGRESS_FILE = ISSUES_DIR / "progress.jsonl"


def load_index() -> Dict:
    """加载 Issue 索引"""
    if not INDEX_FILE.exists():
        return {"next_id": 1, "issues": []}
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_issue_content(file_path: str) -> Optional[Dict]:
    """加载 Issue 文件内容（Markdown + YAML frontmatter）"""
    full_path = BASE_DIR / file_path
    if not full_path.exists():
        return None
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析 YAML frontmatter 和 Markdown body
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            # frontmatter = parts[1]  # 已经在 index.json 中有了
            body = parts[2].strip()
            return {"body": body}
    
    return {"body": content}


def load_progress() -> List[Dict]:
    """加载进度日志"""
    if not PROGRESS_FILE.exists():
        return []
    
    progress_list = []
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    progress_list.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    return progress_list


def load_deliverables() -> Dict:
    """加载交付物索引"""
    deliverables_index = ISSUES_DIR / "deliverables" / "index.json"
    if not deliverables_index.exists():
        return {}
    
    with open(deliverables_index, 'r', encoding='utf-8') as f:
        return json.load(f)


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/issues', methods=['GET'])
def get_issues():
    """获取 Issue 列表
    
    Query Parameters:
    - status: 按状态过滤 (open, in-progress, closed)
    - priority: 按优先级过滤 (P0, P1, P2, P3)
    - assignee: 按负责人过滤
    - labels: 按标签过滤（逗号分隔）
    """
    index = load_index()
    issues = index.get("issues", [])
    
    # 过滤
    status = request.args.get('status')
    priority = request.args.get('priority')
    assignee = request.args.get('assignee')
    labels = request.args.get('labels')
    
    if status:
        issues = [i for i in issues if i.get('status') == status]
    
    if priority:
        issues = [i for i in issues if i.get('priority') == priority]
    
    if assignee:
        issues = [i for i in issues if i.get('assignee') == assignee]
    
    if labels:
        label_list = [l.strip() for l in labels.split(',')]
        issues = [i for i in issues if any(l in i.get('labels', []) for l in label_list)]
    
    return jsonify({
        "total": len(issues),
        "issues": issues
    })


@app.route('/api/issues/<int:issue_id>', methods=['GET'])
def get_issue(issue_id: int):
    """获取单个 Issue 详情"""
    index = load_index()
    issues = index.get("issues", [])
    
    # 查找 Issue
    issue = next((i for i in issues if i.get('id') == issue_id), None)
    if not issue:
        return jsonify({"error": "Issue not found"}), 404
    
    # 加载完整内容
    file_path = issue.get('file')
    if file_path:
        content = load_issue_content(file_path)
        if content:
            issue['body'] = content.get('body', '')
    
    # 加载进度记录
    all_progress = load_progress()
    issue_progress = [p for p in all_progress if p.get('issue_id') == issue_id]
    issue['progress_history'] = issue_progress
    
    # 加载交付物
    deliverables = load_deliverables()
    issue_key = f"issue-{issue_id:03d}"
    issue['deliverables'] = deliverables.get(issue_key, [])
    
    return jsonify(issue)


@app.route('/api/progress', methods=['GET'])
def get_progress():
    """获取进度记录
    
    Query Parameters:
    - issue_id: 按 Issue ID 过滤
    - agent: 按 Agent 过滤
    - limit: 限制返回数量（默认 100）
    """
    all_progress = load_progress()
    
    # 过滤
    issue_id = request.args.get('issue_id', type=int)
    agent = request.args.get('agent')
    limit = request.args.get('limit', type=int, default=100)
    
    if issue_id:
        all_progress = [p for p in all_progress if p.get('issue_id') == issue_id]
    
    if agent:
        all_progress = [p for p in all_progress if p.get('agent') == agent]
    
    # 按时间倒序排列
    all_progress.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # 限制数量
    all_progress = all_progress[:limit]
    
    return jsonify({
        "total": len(all_progress),
        "progress": all_progress
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    index = load_index()
    issues = index.get("issues", [])
    
    # 按状态统计
    status_counts = {}
    for issue in issues:
        status = issue.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # 按优先级统计
    priority_counts = {}
    for issue in issues:
        priority = issue.get('priority', 'unknown')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    # 按负责人统计
    assignee_counts = {}
    for issue in issues:
        assignee = issue.get('assignee', 'unassigned')
        if assignee:
            assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
    
    # 按标签统计
    label_counts = {}
    for issue in issues:
        for label in issue.get('labels', []):
            label_counts[label] = label_counts.get(label, 0) + 1
    
    return jsonify({
        "total": len(issues),
        "by_status": status_counts,
        "by_priority": priority_counts,
        "by_assignee": assignee_counts,
        "by_label": label_counts
    })


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """获取所有 Agent 列表及其任务统计"""
    index = load_index()
    issues = index.get("issues", [])
    
    agents = {}
    for issue in issues:
        assignee = issue.get('assignee')
        if not assignee:
            continue
        
        if assignee not in agents:
            agents[assignee] = {
                "name": assignee,
                "total": 0,
                "open": 0,
                "in_progress": 0,
                "closed": 0
            }
        
        agents[assignee]["total"] += 1
        status = issue.get('status', 'unknown')
        if status == 'open':
            agents[assignee]["open"] += 1
        elif status == 'in-progress':
            agents[assignee]["in_progress"] += 1
        elif status == 'closed':
            agents[assignee]["closed"] += 1
    
    return jsonify({
        "total": len(agents),
        "agents": list(agents.values())
    })


if __name__ == '__main__':
    # 开发模式
    port = 5001  # 避免与 AirPlay Receiver 冲突
    print("🚀 Starting Async Issue Manager Web Dashboard API...")
    print(f"📂 Issues directory: {ISSUES_DIR}")
    print(f"🌐 API will be available at: http://localhost:{port}")
    print("\nAvailable endpoints:")
    print("  GET /api/health          - Health check")
    print("  GET /api/issues          - List all issues")
    print("  GET /api/issues/<id>     - Get issue details")
    print("  GET /api/progress        - Get progress records")
    print("  GET /api/stats           - Get statistics")
    print("  GET /api/agents          - Get agents list")
    print("\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
