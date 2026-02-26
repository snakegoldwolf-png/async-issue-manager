#!/usr/bin/env python3
"""修复 memory_indexer.py 的默认路径问题"""

import os
from pathlib import Path

# 找到所有 memory_indexer.py 文件
workspaces = [
    "workspace-haire",
    "workspace-hunter", 
    "workspace-memo",
    "workspace",
    "workspace-xiaohong",
    "workspace-anna",
    "workspace-dev",
    "workspace-filer",
    "workspace-muse",
    "workspace-webby",
    "workspace-prad",
    "workspace-debugger"
]

base_dir = Path(os.path.expanduser("~/.openclaw"))

# 旧代码
old_code = '''def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="记忆索引系统")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # build 命令
    build_parser = subparsers.add_parser("build", help="构建索引")
    build_parser.add_argument("--workspace", default=os.path.expanduser("~/.openclaw/workspace"), help="工作区目录")
    
    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索记忆")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("--workspace", default=os.path.expanduser("~/.openclaw/workspace"), help="工作区目录")
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="查看统计信息")
    stats_parser.add_argument("--workspace", default=os.path.expanduser("~/.openclaw/workspace"), help="工作区目录")'''

# 新代码 - 自动检测脚本所在的 workspace
new_code = '''def get_default_workspace():
    """自动检测脚本所在的 workspace 目录"""
    script_dir = Path(__file__).resolve().parent
    # 脚本在 workspace/scripts/ 下，所以父目录就是 workspace
    workspace_dir = script_dir.parent
    return str(workspace_dir)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="记忆索引系统")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    default_workspace = get_default_workspace()
    
    # build 命令
    build_parser = subparsers.add_parser("build", help="构建索引")
    build_parser.add_argument("--workspace", default=default_workspace, help="工作区目录")
    
    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索记忆")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("--workspace", default=default_workspace, help="工作区目录")
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="查看统计信息")
    stats_parser.add_argument("--workspace", default=default_workspace, help="工作区目录")'''

fixed_count = 0
for ws in workspaces:
    file_path = base_dir / ws / "scripts" / "memory_indexer.py"
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_code in content:
            new_content = content.replace(old_code, new_code)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 已修复: {file_path}")
            fixed_count += 1
        elif "get_default_workspace" in content:
            print(f"⏭️ 已是最新: {file_path}")
        else:
            print(f"⚠️ 格式不匹配: {file_path}")
    else:
        print(f"❌ 文件不存在: {file_path}")

print(f"\n📊 总计修复: {fixed_count} 个文件")
