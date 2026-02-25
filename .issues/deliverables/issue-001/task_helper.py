#!/usr/bin/env python3
"""
任务助手 - 简化任务追踪和通知的包装器
提供更友好的 API 供 Agent 使用
"""

import sys
import os
from pathlib import Path

# 添加 scripts 目录到 Python 路径
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from task_tracker import TaskTracker
from task_notifier import notify_completion, send_notification


class TaskHelper:
    """任务助手 - 简化的任务管理接口"""
    
    def __init__(self):
        self.tracker = TaskTracker()
    
    def start_task(
        self,
        title: str,
        assignee: str,
        estimated_minutes: int = 30,
        issue_id: str = None
    ) -> str:
        """
        开始一个新任务
        
        Args:
            title: 任务标题
            assignee: 负责人
            estimated_minutes: 预计耗时（分钟）
            issue_id: 关联的 Issue ID
        
        Returns:
            任务 ID
        """
        estimated_duration = estimated_minutes * 60
        task_id = self.tracker.create_task(title, assignee, estimated_duration, issue_id)
        
        print(f"""
📋 任务已启动
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
任务 ID: {task_id}
标题: {title}
负责人: {assignee}
预计耗时: {estimated_minutes} 分钟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 提示：
- 完成后运行: task-helper.py complete {task_id} "完成说明"
- 失败时运行: task-helper.py fail {task_id} "失败原因"
""")
        
        return task_id
    
    def complete_task(self, task_id: str, result: str = "", notify: bool = True):
        """
        完成任务
        
        Args:
            task_id: 任务 ID
            result: 完成说明
            notify: 是否发送通知
        """
        success = self.tracker.update_task(task_id, "completed", result)
        
        if success and notify:
            print("\n📤 发送完成通知...")
            notify_completion(task_id)
    
    def fail_task(self, task_id: str, error: str = "", notify: bool = True):
        """
        标记任务失败
        
        Args:
            task_id: 任务 ID
            error: 失败原因
            notify: 是否发送通知
        """
        success = self.tracker.update_task(task_id, "failed", error=error)
        
        if success and notify:
            print("\n📤 发送失败通知...")
            notify_completion(task_id)
    
    def check_task(self, task_id: str):
        """查看任务状态"""
        task_data = self.tracker.get_task(task_id)
        if task_data:
            print(self.tracker.format_task_info(task_data))
        else:
            print(f"❌ 任务不存在: {task_id}")
    
    def list_tasks(self):
        """列出所有运行中的任务"""
        tasks = self.tracker.list_running_tasks()
        if tasks:
            print(f"📋 运行中的任务 ({len(tasks)})：\n")
            for task_data in tasks:
                print(self.tracker.format_task_info(task_data))
                print("-" * 50)
        else:
            print("✅ 没有运行中的任务")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="任务助手")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # start 命令
    start_parser = subparsers.add_parser("start", help="开始任务")
    start_parser.add_argument("title", help="任务标题")
    start_parser.add_argument("assignee", help="负责人")
    start_parser.add_argument("--minutes", type=int, default=30, help="预计耗时（分钟）")
    start_parser.add_argument("--issue", help="关联的 Issue ID")
    
    # complete 命令
    complete_parser = subparsers.add_parser("complete", help="完成任务")
    complete_parser.add_argument("task_id", help="任务 ID")
    complete_parser.add_argument("result", nargs="?", default="", help="完成说明")
    complete_parser.add_argument("--no-notify", action="store_true", help="不发送通知")
    
    # fail 命令
    fail_parser = subparsers.add_parser("fail", help="标记任务失败")
    fail_parser.add_argument("task_id", help="任务 ID")
    fail_parser.add_argument("error", nargs="?", default="", help="失败原因")
    fail_parser.add_argument("--no-notify", action="store_true", help="不发送通知")
    
    # check 命令
    check_parser = subparsers.add_parser("check", help="查看任务状态")
    check_parser.add_argument("task_id", help="任务 ID")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出运行中的任务")
    
    args = parser.parse_args()
    helper = TaskHelper()
    
    if args.command == "start":
        helper.start_task(args.title, args.assignee, args.minutes, args.issue)
    
    elif args.command == "complete":
        helper.complete_task(args.task_id, args.result, not args.no_notify)
    
    elif args.command == "fail":
        helper.fail_task(args.task_id, args.error, not args.no_notify)
    
    elif args.command == "check":
        helper.check_task(args.task_id)
    
    elif args.command == "list":
        helper.list_tasks()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
