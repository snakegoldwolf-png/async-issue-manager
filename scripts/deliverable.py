#!/usr/bin/env python3
"""
交付物管理工具
确保每个 Issue 关闭时都有明确的交付物存放在 .issues/deliverables/ 目录

用法:
  python3 deliverable.py add <issue_id> --file <path> [--description "说明"]
  python3 deliverable.py list [--issue <id>]
  python3 deliverable.py check <issue_id>  # 检查是否有交付物
"""

import sys
import json
import shutil
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
DELIVERABLES_DIR = WORKSPACE / ".issues" / "deliverables"
DELIVERABLES_INDEX = DELIVERABLES_DIR / "index.json"


class DeliverableManager:
    def __init__(self):
        self.workspace = WORKSPACE
        self.deliverables_dir = DELIVERABLES_DIR
        self.index_file = DELIVERABLES_INDEX
        
        # 确保目录存在
        self.deliverables_dir.mkdir(parents=True, exist_ok=True)
        
        self.load_index()
    
    def load_index(self):
        """加载交付物索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.index = {"deliverables": []}
        else:
            self.index = {"deliverables": []}
    
    def save_index(self):
        """保存交付物索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def add(self, issue_id, file_path, description=""):
        """添加交付物"""
        source = Path(file_path)
        if not source.exists():
            print(f"❌ 文件不存在: {file_path}")
            return None
        
        # 创建 Issue 专属目录
        issue_dir = self.deliverables_dir / f"issue-{issue_id:03d}"
        issue_dir.mkdir(exist_ok=True)
        
        # 复制文件到交付物目录
        dest = issue_dir / source.name
        if source.is_file():
            shutil.copy2(source, dest)
        elif source.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(source, dest)
        
        # 记录到索引
        entry = {
            "issue_id": issue_id,
            "filename": source.name,
            "path": str(dest.relative_to(self.workspace)),
            "description": description,
            "added_at": datetime.now().isoformat(),
            "size": self._get_size(dest)
        }
        
        self.index["deliverables"].append(entry)
        self.save_index()
        
        print(f"✅ 交付物已添加到 Issue #{issue_id}")
        print(f"   文件: {source.name}")
        print(f"   位置: {dest.relative_to(self.workspace)}")
        return entry
    
    def list_deliverables(self, issue_id=None):
        """列出交付物"""
        deliverables = self.index["deliverables"]
        
        if issue_id:
            deliverables = [d for d in deliverables if d["issue_id"] == issue_id]
        
        if not deliverables:
            if issue_id:
                print(f"📋 Issue #{issue_id} 暂无交付物")
            else:
                print("📋 暂无交付物")
            return []
        
        print(f"\n📦 交付物列表 ({len(deliverables)} 个)\n")
        print("=" * 80)
        
        for d in deliverables:
            issue_id = d["issue_id"]
            filename = d["filename"]
            desc = d.get("description", "")
            added_at = d.get("added_at", "")[:19]
            size = d.get("size", "")
            
            print(f"  Issue #{issue_id:03d}: {filename}")
            if desc:
                print(f"    说明: {desc}")
            print(f"    时间: {added_at} | 大小: {size}")
            print()
        
        return deliverables
    
    def check(self, issue_id):
        """检查 Issue 是否有交付物"""
        deliverables = [d for d in self.index["deliverables"] if d["issue_id"] == issue_id]
        
        if deliverables:
            print(f"✅ Issue #{issue_id} 有 {len(deliverables)} 个交付物")
            for d in deliverables:
                print(f"   - {d['filename']}")
            return True
        else:
            print(f"❌ Issue #{issue_id} 没有交付物")
            print(f"   请使用 deliverable.py add {issue_id} --file <path> 添加交付物")
            return False
    
    def _get_size(self, path):
        """获取文件或目录大小"""
        if path.is_file():
            size = path.stat().st_size
            return self._format_size(size)
        elif path.is_dir():
            total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            return self._format_size(total)
        return "0 B"
    
    def _format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


def main():
    parser = argparse.ArgumentParser(description="交付物管理工具")
    sub = parser.add_subparsers(dest="cmd")
    
    # add
    p = sub.add_parser("add", help="添加交付物")
    p.add_argument("issue_id", type=int)
    p.add_argument("--file", required=True, help="文件或目录路径")
    p.add_argument("--description", default="", help="交付物说明")
    
    # list
    p = sub.add_parser("list", help="列出交付物")
    p.add_argument("--issue", type=int, help="按 Issue ID 过滤")
    
    # check
    p = sub.add_parser("check", help="检查 Issue 是否有交付物")
    p.add_argument("issue_id", type=int)
    
    args = parser.parse_args()
    mgr = DeliverableManager()
    
    if args.cmd == "add":
        mgr.add(args.issue_id, args.file, args.description)
    elif args.cmd == "list":
        mgr.list_deliverables(getattr(args, 'issue', None))
    elif args.cmd == "check":
        mgr.check(args.issue_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
