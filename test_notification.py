#!/usr/bin/env python3
"""测试通知功能"""
import sys
sys.path.insert(0, 'scripts')
from monitor import TaskMonitor

# 创建一个测试 alert
test_alerts = [
    {
        "issue_id": 1,
        "title": "实现 1 个未完成功能",
        "assignee": "debugger",
        "type": "stale_progress",
        "elapsed_hours": 0.1,
        "last_progress": "已实现通知功能"
    }
]

monitor = TaskMonitor()
print("测试通知功能...")
monitor.send_notifications(test_alerts)
