#!/usr/bin/env python3
"""
任务进度同步工具
定期更新任务进度到公共日志，方便所有 Agent 查看

用法:
  python3 sync_progress.py update <issue_id> --progress "进度描述" [--status in-progress|blocked|review]
  python3 sync_progress.py view [--issue <id>] [--agent <name>]
  python3 sync_progress.py summary
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import argparse

# 自动检测工作区根目录
import os
def find_workspace():
    # 1. 优先使用共享目录
    shared_ws = Path.home() / ".openclaw" / "shared" / "async-issue-manager"
    if shared_ws.exists():
        return shared_ws
    
    env_ws = os.environ.get("WORKSPACE") or os.environ.get("OPENCLAW_WORKSPACE")
    if env_ws and Path(env_ws).exists():
        return Path(env_ws)
    
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".issues").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    
    return Path.cwd()

WORKSPACE = find_workspace()
PROGRESS_LOG = WORKSPACE / ".issues" / "progress.jsonl"


class ProgressTracker:
    def __init__(self):
        self.workspace = WORKSPACE
        self.log_file = PROGRESS_LOG
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def update(self, issue_id, progress, status=None, agent=None):
        """更新任务进度"""
        entry = {
            "issue_id": issue_id,
            "timestamp": datetime.now().isoformat(),
            "progress": progress,
        }
        
        if status:
            entry["status"] = status
        if agent:
            entry["agent"] = agent
        
        # 追加到 JSONL 文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"✅ Issue #{issue_id} 进度已更新")
        return entry
    
    def view(self, issue_id=None, agent=None, limit=50):
        """查看进度日志"""
        if not self.log_file.exists():
            print("📋 暂无进度记录")
            return []
        
        entries = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if issue_id and entry.get("issue_id") != issue_id:
                        continue
                    if agent and entry.get("agent") != agent:
                        continue
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        # 只返回最近的 N 条
        entries = entries[-limit:]
        
        if not entries:
            print("📋 没有匹配的进度记录")
            return []
        
        print(f"\n📊 进度记录 (最近 {len(entries)} 条)\n")
        print("=" * 80)
        
        for entry in entries:
            issue_id = entry.get("issue_id", "?")
            timestamp = entry.get("timestamp", "")[:19]  # 去掉毫秒
            progress = entry.get("progress", "")
            status = entry.get("status", "")
            agent = entry.get("agent", "")
            
            status_emoji = {
                "in-progress": "🔄",
                "blocked": "🚫",
                "review": "👀",
            }.get(status, "📝")
            
            print(f"{status_emoji} Issue #{issue_id} | {timestamp}")
            if agent:
                print(f"   Agent: {agent}")
            if status:
                print(f"   状态: {status}")
            print(f"   进度: {progress}")
            print("-" * 80)
        
        return entries
    
    def summary(self):
        """生成进度摘要"""
        if not self.log_file.exists():
            print("📋 暂无进度记录")
            return
        
        # 统计每个 Issue 的最新状态
        issue_status = {}
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    issue_id = entry.get("issue_id")
                    if issue_id:
                        issue_status[issue_id] = entry
                except json.JSONDecodeError:
                    continue
        
        if not issue_status:
            print("📋 暂无进度记录")
            return
        
        print(f"\n📊 任务进度摘要 (共 {len(issue_status)} 个任务)\n")
        print("=" * 80)
        
        for issue_id, entry in sorted(issue_status.items()):
            timestamp = entry.get("timestamp", "")[:19]
            progress = entry.get("progress", "")
            status = entry.get("status", "in-progress")
            agent = entry.get("agent", "未分配")
            
            status_emoji = {
                "in-progress": "🔄",
                "blocked": "🚫",
                "review": "👀",
            }.get(status, "📝")
            
            print(f"{status_emoji} Issue #{issue_id} | {agent} | {timestamp}")
            print(f"   {progress}")
            print("-" * 80)


def main():
    parser = argparse.ArgumentParser(description="任务进度同步工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # update 命令
    update_parser = subparsers.add_parser("update", help="更新进度")
    update_parser.add_argument("issue_id", type=int, help="Issue ID")
    update_parser.add_argument("--progress", required=True, help="进度描述")
    update_parser.add_argument("--status", choices=["in-progress", "blocked", "review"], help="状态")
    update_parser.add_argument("--agent", help="Agent 名称")
    
    # view 命令
    view_parser = subparsers.add_parser("view", help="查看进度")
    view_parser.add_argument("--issue", type=int, help="过滤 Issue ID")
    view_parser.add_argument("--agent", help="过滤 Agent")
    view_parser.add_argument("--limit", type=int, default=50, help="显示条数")
    
    # summary 命令
    subparsers.add_parser("summary", help="进度摘要")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    tracker = ProgressTracker()
    
    if args.command == "update":
        tracker.update(
            args.issue_id,
            args.progress,
            status=args.status,
            agent=args.agent
        )
    
    elif args.command == "view":
        tracker.view(
            issue_id=args.issue,
            agent=args.agent,
            limit=args.limit
        )
    
    elif args.command == "summary":
        tracker.summary()


if __name__ == "__main__":
    main()
