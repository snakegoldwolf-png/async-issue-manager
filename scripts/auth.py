#!/usr/bin/env python3
"""
权限控制模块
只有授权用户可以创建 Issue，Agent 只能更新进度
"""

import os
import sys
from pathlib import Path

# 授权创建 Issue 的用户列表
AUTHORIZED_CREATORS = [
    "bro",
    "loryoncloud",
    "admin",
]

# 从环境变量获取当前用户
def get_current_user():
    """获取当前用户身份"""
    # 优先使用 OPENCLAW_USER 环境变量
    user = os.environ.get("OPENCLAW_USER")
    if user:
        return user
    
    # 其次使用 USER 环境变量
    user = os.environ.get("USER")
    if user:
        return user
    
    # 最后使用系统用户名
    import getpass
    return getpass.getuser()


def check_create_permission():
    """检查是否有创建 Issue 的权限"""
    current_user = get_current_user()
    
    if current_user in AUTHORIZED_CREATORS:
        return True, current_user
    
    return False, current_user


def require_create_permission():
    """装饰器：要求创建权限"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            allowed, user = check_create_permission()
            if not allowed:
                print(f"❌ 权限不足: 用户 '{user}' 无权创建 Issue")
                print(f"   只有以下用户可以创建 Issue: {', '.join(AUTHORIZED_CREATORS)}")
                print(f"   Agent 只能通过 sync_progress.py 更新任务进度")
                sys.exit(1)
            return func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试权限检查
    allowed, user = check_create_permission()
    if allowed:
        print(f"✅ 用户 '{user}' 有创建 Issue 的权限")
    else:
        print(f"❌ 用户 '{user}' 无权创建 Issue")
        print(f"   授权用户: {', '.join(AUTHORIZED_CREATORS)}")
