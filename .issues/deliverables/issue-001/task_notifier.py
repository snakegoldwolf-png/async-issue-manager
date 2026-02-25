#!/usr/bin/env python3
"""
任务通知器 - 自动发送任务完成/失败通知
配合 cron 使用，定期检查任务状态并发送通知
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess

TASKS_DIR = Path.home() / ".openclaw" / "workspace" / ".tasks"
BRO_OPEN_ID = "ou_4f4b38f9046a497c4b26434bfc98808c"


def load_task(task_id: str) -> dict:
    """加载任务数据"""
    task_file = TASKS_DIR / f"{task_id}.json"
    
    if not task_file.exists():
        # 检查归档目录
        for subdir in ["completed", "failed"]:
            archived_file = TASKS_DIR / subdir / f"{task_id}.json"
            if archived_file.exists():
                task_file = archived_file
                break
    
    if not task_file.exists():
        return None
    
    with open(task_file, 'r') as f:
        return json.load(f)


def format_duration(seconds: int) -> str:
    """格式化时长"""
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} 分钟"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours} 小时 {remaining_minutes} 分钟"


def send_notification(message: str):
    """发送飞书通知"""
    # 使用 OpenClaw 的 message 工具
    cmd = [
        "openclaw", "message", "send",
        "--target", BRO_OPEN_ID,
        "--message", message
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ 通知已发送")
            return True
        else:
            print(f"❌ 通知发送失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 通知发送异常: {e}")
        return False


def notify_completion(task_id: str):
    """发送任务完成通知"""
    task_data = load_task(task_id)
    if not task_data:
        print(f"❌ 任务不存在: {task_id}")
        return False
    
    status = task_data.get("status")
    if status not in ["completed", "failed", "timeout"]:
        print(f"⚠️ 任务尚未完成: {task_id} (状态: {status})")
        return False
    
    title = task_data.get("title", "未命名任务")
    assignee = task_data.get("assignee", "未知")
    start_time = task_data.get("startTime", 0)
    end_time = task_data.get("endTime", 0)
    duration = end_time - start_time
    result = task_data.get("result", "")
    error = task_data.get("error", "")
    issue_id = task_data.get("issueId", "")
    
    if status == "completed":
        message = f"""✅ 任务完成：{title}

执行人：{assignee}
耗时：{format_duration(duration)}
结果：{result}

详情：任务 ID {task_id}"""
        
        if issue_id:
            message += f"\n关联 Issue: #{issue_id}"
    
    elif status == "failed":
        message = f"""❌ 任务失败：{title}

执行人：{assignee}
耗时：{format_duration(duration)}
失败原因：{error}

详情：任务 ID {task_id}"""
        
        if issue_id:
            message += f"\n关联 Issue: #{issue_id}"
    
    elif status == "timeout":
        message = f"""⏰ 任务超时：{title}

执行人：{assignee}
已运行：{format_duration(duration)}
超时原因：{error}

详情：任务 ID {task_id}"""
        
        if issue_id:
            message += f"\n关联 Issue: #{issue_id}"
    
    return send_notification(message)


def check_all_tasks():
    """检查所有运行中的任务"""
    print("🔍 检查运行中的任务...")
    
    task_files = list(TASKS_DIR.glob("task-*.json"))
    if not task_files:
        print("✅ 没有运行中的任务")
        return
    
    print(f"📋 发现 {len(task_files)} 个运行中的任务")
    
    for task_file in task_files:
        task_id = task_file.stem
        with open(task_file, 'r') as f:
            task_data = json.load(f)
        
        status = task_data.get("status")
        title = task_data.get("title", "未命名任务")
        
        print(f"  - {task_id}: {title} (状态: {status})")
        
        # 如果任务已完成/失败，发送通知
        if status in ["completed", "failed", "timeout"]:
            print(f"    → 发送通知...")
            notify_completion(task_id)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="任务通知器")
    parser.add_argument("--task-id", help="指定任务 ID")
    parser.add_argument("--check-all", action="store_true", help="检查所有任务")
    
    args = parser.parse_args()
    
    if args.task_id:
        notify_completion(args.task_id)
    elif args.check_all:
        check_all_tasks()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
