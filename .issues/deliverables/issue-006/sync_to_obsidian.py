#!/usr/bin/env python3
"""
OpenClaw Obsidian 同步脚本

将 Agent 产出内容同步到 Obsidian Vault

用法:
    python3 sync_to_obsidian.py --content "内容" --type diary --agent filer
    python3 sync_to_obsidian.py --file /path/to/file.md --type knowledge
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Vault 根目录
VAULT_ROOT = Path.home() / ".openclaw" / "shared" / "obsidian-vault"

# 路由规则
ROUTING_RULES = {
    "diary": "01-Agent/{agent}/学习日记",
    "work": "01-Agent/{agent}/工作记录",
    "knowledge": "02-记忆库/语义记忆/技术",
    "methodology": "02-记忆库/语义记忆/方法论",
    "tool": "02-记忆库/语义记忆/工具",
    "rule": "02-记忆库/强制规则",
    "event": "02-记忆库/情景记忆/2026/02-February",
    "task": "03-任务管理/Issue追踪/in-progress",
    "task_closed": "03-任务管理/Issue追踪/closed",
    "meeting": "05-团队协作/会议记录/每日站会",
    "decision": "05-团队协作/决策记录",
    "article": "06-资源库/参考资料/文章",
    "tweet": "06-资源库/参考资料/推文",
    "code": "06-资源库/代码片段",
}

# Agent 列表
AGENTS = [
    "filer", "debugger", "webby", "anna", "memo",
    "muse", "prad", "haire", "xiaohong", "hunter", "dev"
]


def get_target_path(content_type: str, agent: str = None, filename: str = None) -> Path:
    """根据内容类型和 Agent 获取目标路径"""
    if content_type not in ROUTING_RULES:
        # 默认路由到 Agent 工作记录
        if agent:
            target_dir = f"01-Agent/{agent}/工作记录"
        else:
            target_dir = "02-记忆库/语义记忆/技术"
    else:
        target_dir = ROUTING_RULES[content_type]
    
    # 替换 agent 占位符
    if "{agent}" in target_dir:
        if not agent:
            agent = "unknown"
        target_dir = target_dir.replace("{agent}", agent.capitalize())
    
    target_path = VAULT_ROOT / target_dir
    
    # 生成文件名
    if not filename:
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today}.md"
    elif not filename.endswith(".md"):
        filename = f"{filename}.md"
    
    return target_path / filename


def generate_frontmatter(title: str, author: str, content_type: str, tags: list = None) -> str:
    """生成 Frontmatter 元数据"""
    now = datetime.now().isoformat()
    
    frontmatter = f"""---
title: {title}
created: {now}
updated: {now}
author: {author}
type: {content_type}
"""
    
    if tags:
        frontmatter += "tags:\n"
        for tag in tags:
            frontmatter += f"  - {tag}\n"
    
    frontmatter += "---\n\n"
    return frontmatter


def sync_content(
    content: str,
    content_type: str,
    agent: str = None,
    title: str = None,
    filename: str = None,
    tags: list = None,
    append: bool = False
) -> dict:
    """同步内容到 Obsidian Vault"""
    
    # 获取目标路径
    target_path = get_target_path(content_type, agent, filename)
    
    # 确保目录存在
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 生成标题
    if not title:
        title = filename.replace(".md", "") if filename else datetime.now().strftime("%Y-%m-%d")
    
    # 处理内容
    if append and target_path.exists():
        # 追加模式
        with open(target_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n{content}")
        mode = "appended"
    else:
        # 覆盖或新建
        if not content.startswith("---"):
            # 添加 frontmatter
            content = generate_frontmatter(title, agent or "system", content_type, tags) + content
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        mode = "created" if not target_path.exists() else "updated"
    
    return {
        "status": "success",
        "mode": mode,
        "path": str(target_path),
        "type": content_type,
        "agent": agent
    }


def sync_file(source_path: str, content_type: str, agent: str = None) -> dict:
    """同步文件到 Obsidian Vault"""
    source = Path(source_path)
    
    if not source.exists():
        return {"status": "error", "message": f"Source file not found: {source_path}"}
    
    with open(source, "r", encoding="utf-8") as f:
        content = f.read()
    
    return sync_content(
        content=content,
        content_type=content_type,
        agent=agent,
        filename=source.name
    )


def sync_diary(agent: str, content: str) -> dict:
    """同步 Agent 日记"""
    today = datetime.now().strftime("%Y-%m-%d")
    return sync_content(
        content=content,
        content_type="diary",
        agent=agent,
        title=f"{today} 学习日记",
        filename=f"{today}.md",
        tags=["日记", "学习"]
    )


def sync_issue(issue_id: int, title: str, content: str, status: str = "in-progress") -> dict:
    """同步 Issue 到 Obsidian"""
    content_type = "task_closed" if status == "closed" else "task"
    return sync_content(
        content=content,
        content_type=content_type,
        title=f"Issue-{issue_id}: {title}",
        filename=f"Issue-{issue_id:03d}.md",
        tags=["任务", f"Issue-{issue_id}", status]
    )


def sync_meeting(date: str, content: str, meeting_type: str = "standup") -> dict:
    """同步会议记录"""
    return sync_content(
        content=content,
        content_type="meeting",
        title=f"{date} {meeting_type}",
        filename=f"{date}-{meeting_type}.md",
        tags=["会议", meeting_type]
    )


def list_vault_structure() -> dict:
    """列出 Vault 目录结构"""
    structure = {}
    
    for root, dirs, files in os.walk(VAULT_ROOT):
        rel_path = Path(root).relative_to(VAULT_ROOT)
        if str(rel_path) == ".":
            rel_path = ""
        
        structure[str(rel_path)] = {
            "dirs": dirs,
            "files": files
        }
    
    return structure


def main():
    parser = argparse.ArgumentParser(description="OpenClaw Obsidian 同步脚本")
    parser.add_argument("--content", "-c", help="要同步的内容")
    parser.add_argument("--file", "-f", help="要同步的文件路径")
    parser.add_argument("--type", "-t", required=True, help="内容类型", choices=list(ROUTING_RULES.keys()))
    parser.add_argument("--agent", "-a", help="Agent 名称", choices=AGENTS)
    parser.add_argument("--title", help="文档标题")
    parser.add_argument("--filename", help="目标文件名")
    parser.add_argument("--tags", nargs="+", help="标签列表")
    parser.add_argument("--append", action="store_true", help="追加模式")
    parser.add_argument("--list", action="store_true", help="列出 Vault 结构")
    
    args = parser.parse_args()
    
    if args.list:
        structure = list_vault_structure()
        print(json.dumps(structure, indent=2, ensure_ascii=False))
        return
    
    if args.file:
        result = sync_file(args.file, args.type, args.agent)
    elif args.content:
        result = sync_content(
            content=args.content,
            content_type=args.type,
            agent=args.agent,
            title=args.title,
            filename=args.filename,
            tags=args.tags,
            append=args.append
        )
    else:
        print("错误: 必须提供 --content 或 --file 参数")
        sys.exit(1)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result["status"] == "success":
        print(f"\n✅ 同步成功: {result['path']}")
    else:
        print(f"\n❌ 同步失败: {result.get('message', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
