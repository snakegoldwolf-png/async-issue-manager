#!/usr/bin/env python3
"""
任务追踪系统 - Python 版本
提供更强大的任务管理功能
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

TASKS_DIR = Path.home() / ".openclaw" / "workspace" / ".tasks"
TASKS_DIR.mkdir(parents=True, exist_ok=True)
(TASKS_DIR / "completed").mkdir(exist_ok=True)
(TASKS_DIR / "failed").mkdir(exist_ok=True)


class TaskTracker:
    """任务追踪器"""
    
    def __init__(self):
        self.tasks_dir = TASKS_DIR
    
    def create_task(
        self,
        title: str,
        assignee: str,
        estimated_duration: int = 1800,
        issue_id: Optional[str] = None
    ) -> str:
        """创建新任务"""
        timestamp = int(time.time())
        task_id = f"task-{timestamp}"
        task_file = self.tasks_dir / f"{task_id}.json"
        
        task_data = {
            "id": task_id,
            "title": title,
            "assignee": assignee,
            "startTime": timestamp,
            "estimatedDuration": estimated_duration,
            "status": "running",
            "issueId": issue_id or ""
        }
        
        with open(task_file, 'w') as f:
            json.dump(task_data, f, indent=2)
        
        print(f"✅ 任务已创建: {task_id}")
        return task_id
    
    def update_task(
        self,
        task_id: str,
        status: str,
        result: str = "",
        error: str = ""
    ) -> bool:
        """更新任务状态"""
        task_file = self.tasks_dir / f"{task_id}.json"
        
        if not task_file.exists():
            print(f"❌ 任务文件不存在: {task_file}")
            return False
        
        with open(task_file, 'r') as f:
            task_data = json.load(f)
        
        end_time = int(time.time())
        task_data.update({
            "status": status,
            "endTime": end_time,
            "result": result,
            "error": error
        })
        
        with open(task_file, 'w') as f:
            json.dump(task_data, f, indent=2)
        
        # 归档
        if status == "completed":
            target_dir = self.tasks_dir / "completed"
            task_file.rename(target_dir / f"{task_id}.json")
            print(f"✅ 任务已完成并归档: {task_id}")
        elif status in ["failed", "timeout"]:
            target_dir = self.tasks_dir / "failed"
            task_file.rename(target_dir / f"{task_id}.json")
            print(f"❌ 任务已失败并归档: {task_id}")
        else:
            print(f"✅ 任务状态已更新: {status}")
        
        return True
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务信息"""
        # 检查运行中的任务
        task_file = self.tasks_dir / f"{task_id}.json"
        if task_file.exists():
            with open(task_file, 'r') as f:
                return json.load(f)
        
        # 检查已完成的任务
        task_file = self.tasks_dir / "completed" / f"{task_id}.json"
        if task_file.exists():
            with open(task_file, 'r') as f:
                return json.load(f)
        
        # 检查失败的任务
        task_file = self.tasks_dir / "failed" / f"{task_id}.json"
        if task_file.exists():
            with open(task_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def list_running_tasks(self) -> List[Dict]:
        """列出所有运行中的任务"""
        tasks = []
        for task_file in self.tasks_dir.glob("task-*.json"):
            with open(task_file, 'r') as f:
                tasks.append(json.load(f))
        return tasks
    
    def check_timeout(self) -> List[str]:
        """检查超时任务"""
        now = int(time.time())
        timeout_tasks = []
        
        for task_file in self.tasks_dir.glob("task-*.json"):
            with open(task_file, 'r') as f:
                task_data = json.load(f)
            
            task_id = task_data["id"]
            start_time = task_data["startTime"]
            estimated_duration = task_data["estimatedDuration"]
            timeout_threshold = estimated_duration * 2
            elapsed = now - start_time
            
            if elapsed > timeout_threshold:
                print(f"⚠️ 任务超时: {task_id} (已运行 {elapsed // 60} 分钟，预计 {estimated_duration // 60} 分钟)")
                self.update_task(
                    task_id,
                    "timeout",
                    error=f"任务执行时间超过预期的 2 倍 ({elapsed // 60} 分钟)"
                )
                timeout_tasks.append(task_id)
        
        return timeout_tasks
    
    def get_task_duration(self, task_id: str) -> Optional[int]:
        """获取任务执行时长（秒）"""
        task_data = self.get_task(task_id)
        if not task_data:
            return None
        
        start_time = task_data["startTime"]
        end_time = task_data.get("endTime", int(time.time()))
        return end_time - start_time
    
    def format_task_info(self, task_data: Dict) -> str:
        """格式化任务信息"""
        task_id = task_data["id"]
        title = task_data["title"]
        assignee = task_data["assignee"]
        status = task_data["status"]
        start_time = task_data["startTime"]
        
        start_dt = datetime.fromtimestamp(start_time)
        start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
        
        if "endTime" in task_data:
            end_time = task_data["endTime"]
            duration = end_time - start_time
            duration_min = duration // 60
            duration_str = f"{duration_min} 分钟"
        else:
            now = int(time.time())
            elapsed = now - start_time
            elapsed_min = elapsed // 60
            duration_str = f"{elapsed_min} 分钟（进行中）"
        
        info = f"""
任务 ID: {task_id}
标题: {title}
负责人: {assignee}
状态: {status}
开始时间: {start_str}
耗时: {duration_str}
"""
        
        if task_data.get("issueId"):
            info += f"关联 Issue: #{task_data['issueId']}\n"
        
        if task_data.get("result"):
            info += f"结果: {task_data['result']}\n"
        
        if task_data.get("error"):
            info += f"错误: {task_data['error']}\n"
        
        return info.strip()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="任务追踪系统")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # create 命令
    create_parser = subparsers.add_parser("create", help="创建任务")
    create_parser.add_argument("title", help="任务标题")
    create_parser.add_argument("assignee", help="负责人")
    create_parser.add_argument("--duration", type=int, default=1800, help="预计耗时（秒）")
    create_parser.add_argument("--issue", help="关联的 Issue ID")
    
    # update 命令
    update_parser = subparsers.add_parser("update", help="更新任务状态")
    update_parser.add_argument("task_id", help="任务 ID")
    update_parser.add_argument("status", choices=["running", "completed", "failed", "timeout"], help="状态")
    update_parser.add_argument("--result", default="", help="结果说明")
    update_parser.add_argument("--error", default="", help="错误信息")
    
    # check 命令
    check_parser = subparsers.add_parser("check", help="查看任务信息")
    check_parser.add_argument("task_id", help="任务 ID")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出运行中的任务")
    
    # timeout 命令
    timeout_parser = subparsers.add_parser("timeout", help="检查超时任务")
    
    args = parser.parse_args()
    tracker = TaskTracker()
    
    if args.command == "create":
        task_id = tracker.create_task(
            args.title,
            args.assignee,
            args.duration,
            args.issue
        )
        print(f"任务 ID: {task_id}")
    
    elif args.command == "update":
        tracker.update_task(
            args.task_id,
            args.status,
            args.result,
            args.error
        )
    
    elif args.command == "check":
        task_data = tracker.get_task(args.task_id)
        if task_data:
            print(tracker.format_task_info(task_data))
        else:
            print(f"❌ 任务不存在: {args.task_id}")
    
    elif args.command == "list":
        tasks = tracker.list_running_tasks()
        if tasks:
            print(f"📋 运行中的任务 ({len(tasks)})：\n")
            for task_data in tasks:
                print(tracker.format_task_info(task_data))
                print("-" * 50)
        else:
            print("✅ 没有运行中的任务")
    
    elif args.command == "timeout":
        timeout_tasks = tracker.check_timeout()
        if not timeout_tasks:
            print("✅ 没有超时任务")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
