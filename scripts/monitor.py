#!/usr/bin/env python3
"""
任务监控和推进工具
定期检查任务状态，对超时或停滞的任务发出提醒

用法:
  python3 monitor.py check [--timeout-hours 24] [--notify]
  python3 monitor.py status <issue_id>
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
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
ISSUES_DIR = WORKSPACE / ".issues"
PROGRESS_LOG = ISSUES_DIR / "progress.jsonl"


class TaskMonitor:
    def __init__(self):
        self.workspace = WORKSPACE
        self.issues_dir = ISSUES_DIR
        self.progress_log = PROGRESS_LOG
        self.index_file = self.issues_dir / "index.json"
    
    def load_index(self):
        """加载 Issue 索引"""
        if not self.index_file.exists():
            return {"issues": [], "next_id": 1}
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_latest_progress(self, issue_id):
        """获取 Issue 的最新进度"""
        if not self.progress_log.exists():
            return None
        
        latest = None
        with open(self.progress_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("issue_id") == issue_id:
                        latest = entry
                except json.JSONDecodeError:
                    continue
        
        return latest
    
    def check(self, timeout_hours=24, notify=False):
        """检查任务状态，识别超时或停滞的任务"""
        index = self.load_index()
        now = datetime.now()
        
        alerts = []
        
        for issue in index["issues"]:
            if issue.get("status") not in ["open", "in-progress"]:
                continue
            
            issue_id = issue["id"]
            assignee = issue.get("assignee", "unassigned")
            title = issue.get("title", "")
            
            # 检查分配时间
            assigned_at = issue.get("assigned_at")
            if assigned_at:
                assigned_time = datetime.fromisoformat(assigned_at)
                elapsed = (now - assigned_time).total_seconds() / 3600
                
                if elapsed > timeout_hours:
                    # 检查是否有最近的进度更新
                    latest_progress = self.get_latest_progress(issue_id)
                    
                    if latest_progress:
                        progress_time = datetime.fromisoformat(latest_progress["timestamp"])
                        progress_elapsed = (now - progress_time).total_seconds() / 3600
                        
                        if progress_elapsed > timeout_hours / 2:
                            alerts.append({
                                "issue_id": issue_id,
                                "title": title,
                                "assignee": assignee,
                                "type": "stale_progress",
                                "elapsed_hours": round(progress_elapsed, 1),
                                "last_progress": latest_progress.get("progress", ""),
                            })
                    else:
                        alerts.append({
                            "issue_id": issue_id,
                            "title": title,
                            "assignee": assignee,
                            "type": "no_progress",
                            "elapsed_hours": round(elapsed, 1),
                        })
            
            # 检查 open 状态但已分配的任务
            elif issue.get("status") == "open" and assignee != "unassigned":
                created_at = issue.get("created_at")
                if created_at:
                    created_time = datetime.fromisoformat(created_at)
                    elapsed = (now - created_time).total_seconds() / 3600
                    
                    if elapsed > timeout_hours:
                        alerts.append({
                            "issue_id": issue_id,
                            "title": title,
                            "assignee": assignee,
                            "type": "not_started",
                            "elapsed_hours": round(elapsed, 1),
                        })
        
        if not alerts:
            print("✅ 所有任务进展正常")
            return []
        
        print(f"\n⚠️  发现 {len(alerts)} 个需要关注的任务\n")
        print("=" * 80)
        
        for alert in alerts:
            issue_id = alert["issue_id"]
            title = alert["title"]
            assignee = alert["assignee"]
            alert_type = alert["type"]
            elapsed = alert["elapsed_hours"]
            
            if alert_type == "no_progress":
                print(f"🚨 Issue #{issue_id}: {title}")
                print(f"   负责人: {assignee}")
                print(f"   问题: 已分配 {elapsed} 小时，但无进度更新")
                print(f"   建议: 联系 {assignee} 确认任务状态")
            
            elif alert_type == "stale_progress":
                print(f"⏰ Issue #{issue_id}: {title}")
                print(f"   负责人: {assignee}")
                print(f"   问题: 最后更新距今 {elapsed} 小时")
                print(f"   最后进度: {alert['last_progress']}")
                print(f"   建议: 跟进任务进展")
            
            elif alert_type == "not_started":
                print(f"📌 Issue #{issue_id}: {title}")
                print(f"   负责人: {assignee}")
                print(f"   问题: 已创建 {elapsed} 小时，但未开始")
                print(f"   建议: 确认是否需要重新分配")
            
            print("-" * 80)
        
        if notify:
            self.send_notifications(alerts)
        
        return alerts
    
    def send_notifications(self, alerts):
        """发送飞书通知给相关负责人"""
        if not alerts:
            return
        
        print("\n📢 发送通知中...")
        
        # 按负责人分组
        by_assignee = {}
        for alert in alerts:
            assignee = alert["assignee"]
            if assignee not in by_assignee:
                by_assignee[assignee] = []
            by_assignee[assignee].append(alert)
        
        # 为每个负责人发送通知
        for assignee, assignee_alerts in by_assignee.items():
            if assignee == "unassigned":
                continue
            
            message = self._format_notification(assignee, assignee_alerts)
            
            try:
                # 使用 sessions_send 发送消息
                import subprocess
                result = subprocess.run(
                    ["openclaw", "sessions", "send", "--label", assignee, "--message", message],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print(f"  ✅ 已通知 {assignee} ({len(assignee_alerts)} 个任务)")
                else:
                    print(f"  ⚠️ 通知 {assignee} 失败: {result.stderr.strip()}")
            
            except subprocess.TimeoutExpired:
                print(f"  ⚠️ 通知 {assignee} 超时")
            except Exception as e:
                print(f"  ⚠️ 通知 {assignee} 出错: {e}")
    
    def _format_notification(self, assignee, alerts):
        """格式化通知消息"""
        lines = [
            f"🔔 任务提醒 - {assignee}",
            "",
            f"发现 {len(alerts)} 个需要关注的任务：",
            ""
        ]
        
        for alert in alerts:
            issue_id = alert["issue_id"]
            title = alert["title"]
            alert_type = alert["type"]
            elapsed = alert["elapsed_hours"]
            
            if alert_type == "no_progress":
                lines.append(f"🚨 Issue #{issue_id}: {title}")
                lines.append(f"   问题: 已分配 {elapsed} 小时，但无进度更新")
                lines.append(f"   建议: 请更新任务进度或说明遇到的问题")
            
            elif alert_type == "stale_progress":
                lines.append(f"⏰ Issue #{issue_id}: {title}")
                lines.append(f"   问题: 最后更新距今 {elapsed} 小时")
                lines.append(f"   最后进度: {alert['last_progress']}")
                lines.append(f"   建议: 请继续推进或更新状态")
            
            elif alert_type == "not_started":
                lines.append(f"📌 Issue #{issue_id}: {title}")
                lines.append(f"   问题: 已创建 {elapsed} 小时，但未开始")
                lines.append(f"   建议: 请开始处理或说明是否需要重新分配")
            
            lines.append("")
        
        lines.append("---")
        lines.append("💡 使用 `manager.py progress <issue_id> <进度说明>` 更新进度")
        
        return "\n".join(lines)
    
    def status(self, issue_id):
        """查看单个任务的详细状态"""
        index = self.load_index()
        
        issue = None
        for i in index["issues"]:
            if i["id"] == issue_id:
                issue = i
                break
        
        if not issue:
            print(f"❌ Issue #{issue_id} 不存在")
            return
        
        print(f"\n📋 Issue #{issue_id}: {issue.get('title', '')}\n")
        print("=" * 80)
        print(f"状态: {issue.get('status', 'unknown')}")
        print(f"负责人: {issue.get('assignee', 'unassigned')}")
        print(f"优先级: {issue.get('priority', 'P2')}")
        print(f"标签: {', '.join(issue.get('labels', []))}")
        print(f"创建时间: {issue.get('created_at', '')[:19]}")
        
        if issue.get("assigned_at"):
            print(f"分配时间: {issue.get('assigned_at', '')[:19]}")
            
            assigned_time = datetime.fromisoformat(issue["assigned_at"])
            elapsed = (datetime.now() - assigned_time).total_seconds() / 3600
            print(f"已分配: {round(elapsed, 1)} 小时")
        
        print("-" * 80)
        
        # 显示进度历史
        if self.progress_log.exists():
            progress_entries = []
            with open(self.progress_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("issue_id") == issue_id:
                            progress_entries.append(entry)
                    except json.JSONDecodeError:
                        continue
            
            if progress_entries:
                print(f"\n📊 进度历史 ({len(progress_entries)} 条更新):\n")
                for entry in progress_entries[-10:]:  # 只显示最近 10 条
                    timestamp = entry.get("timestamp", "")[:19]
                    progress = entry.get("progress", "")
                    status = entry.get("status", "")
                    
                    status_emoji = {
                        "in-progress": "🔄",
                        "blocked": "🚫",
                        "review": "👀",
                    }.get(status, "📝")
                    
                    print(f"{status_emoji} {timestamp}")
                    print(f"   {progress}")
                    print()
            else:
                print("\n⚠️  暂无进度更新")


def main():
    parser = argparse.ArgumentParser(description="任务监控和推进工具")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # check 命令
    check_parser = subparsers.add_parser("check", help="检查任务状态")
    check_parser.add_argument("--timeout-hours", type=float, default=24, help="超时阈值（小时）")
    check_parser.add_argument("--notify", action="store_true", help="发送通知")
    
    # status 命令
    status_parser = subparsers.add_parser("status", help="查看任务状态")
    status_parser.add_argument("issue_id", type=int, help="Issue ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    monitor = TaskMonitor()
    
    if args.command == "check":
        monitor.check(
            timeout_hours=args.timeout_hours,
            notify=args.notify
        )
    
    elif args.command == "status":
        monitor.status(args.issue_id)


if __name__ == "__main__":
    main()
