#!/usr/bin/env python3
"""
记忆 TTL 管理器 - 实现记忆优先级和自动过期
基于 Hunter 的分析，实现永续 Agent 的记忆生命周期管理
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import shutil


class MemoryTTLManager:
    """记忆 TTL 管理器"""
    
    # TTL 策略（天数）
    TTL_POLICY = {
        "P0": None,      # 永不删除
        "P1": 90,        # 90 天后归档
        "P2": 30,        # 30 天后删除
        "P3": 7          # 7 天后删除
    }
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.memory_file = workspace_dir / "MEMORY.md"
        self.archive_dir = workspace_dir / "memory" / "archive"
        
        # 确保归档目录存在
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_memory_sections(self) -> List[Dict]:
        """解析 MEMORY.md 中的章节"""
        if not self.memory_file.exists():
            return []
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = []
        lines = content.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            # 匹配标题行（带优先级）
            match = re.match(r'^##\s+\[P([0-3])\]\s+(.+)$', line)
            if match:
                # 保存上一个章节
                if current_section:
                    current_section['end_line'] = i - 1
                    sections.append(current_section)
                
                # 开始新章节
                priority = f"P{match.group(1)}"
                title = match.group(2).strip()
                
                # 查找 TTL 注释
                ttl = None
                if i + 1 < len(lines):
                    ttl_match = re.match(r'<!--\s*TTL:\s*(\w+)\s*-->', lines[i + 1])
                    if ttl_match:
                        ttl = ttl_match.group(1)
                
                current_section = {
                    'priority': priority,
                    'title': title,
                    'ttl': ttl,
                    'start_line': i,
                    'end_line': None,
                    'content_lines': []
                }
            elif current_section:
                current_section['content_lines'].append(line)
        
        # 保存最后一个章节
        if current_section:
            current_section['end_line'] = len(lines) - 1
            sections.append(current_section)
        
        return sections
    
    def check_expiration(self, section: Dict) -> Tuple[bool, str]:
        """检查章节是否过期"""
        priority = section['priority']
        ttl = section.get('ttl')
        
        # P0 永不过期
        if priority == "P0" or ttl == "never":
            return False, "永不过期"
        
        # 如果有明确的 TTL 标记，使用它
        if ttl:
            if ttl.endswith('d'):
                days = int(ttl[:-1])
            else:
                return False, f"无效的 TTL: {ttl}"
        else:
            # 使用默认策略
            days = self.TTL_POLICY.get(priority)
            if days is None:
                return False, "永不过期"
        
        # 检查最后修改时间
        # 注意：这里简化处理，实际应该从 git 或文件元数据获取
        # 暂时返回 False，需要进一步实现
        return False, f"TTL: {days} 天（未实现时间检查）"
    
    def add_ttl_markers(self):
        """为 MEMORY.md 中的章节添加 TTL 标记"""
        if not self.memory_file.exists():
            print("❌ MEMORY.md 不存在")
            return
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)
            
            # 检查是否是带优先级的标题
            match = re.match(r'^##\s+\[P([0-3])\]\s+(.+)$', line)
            if match:
                priority = f"P{match.group(1)}"
                
                # 检查下一行是否已有 TTL 标记
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if not re.match(r'<!--\s*TTL:', next_line):
                        # 添加 TTL 标记
                        ttl_value = self._get_ttl_value(priority)
                        new_lines.append(f"<!-- TTL: {ttl_value} -->\n")
            
            i += 1
        
        # 写回文件
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"✅ 已为 MEMORY.md 添加 TTL 标记")
    
    def _get_ttl_value(self, priority: str) -> str:
        """获取 TTL 值"""
        days = self.TTL_POLICY.get(priority)
        if days is None:
            return "never"
        return f"{days}d"
    
    def clean_expired(self, dry_run: bool = True):
        """清理过期记忆"""
        sections = self.parse_memory_sections()
        
        expired_sections = []
        for section in sections:
            is_expired, reason = self.check_expiration(section)
            if is_expired:
                expired_sections.append(section)
        
        if not expired_sections:
            print("✅ 没有过期的记忆")
            return
        
        print(f"⚠️ 发现 {len(expired_sections)} 个过期章节:\n")
        
        for section in expired_sections:
            print(f"  - [{section['priority']}] {section['title']}")
            print(f"    TTL: {section.get('ttl', 'N/A')}")
            print()
        
        if dry_run:
            print("💡 这是预览模式，使用 --execute 执行实际清理")
        else:
            # 实际清理逻辑
            self._archive_sections(expired_sections)
            print("✅ 清理完成")
    
    def _archive_sections(self, sections: List[Dict]):
        """归档章节"""
        # 读取原文件
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 创建归档文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"archived_{timestamp}.md"
        
        with open(archive_file, 'w', encoding='utf-8') as f:
            f.write(f"# 归档记忆 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for section in sections:
                start = section['start_line']
                end = section['end_line']
                f.writelines(lines[start:end+1])
                f.write("\n\n---\n\n")
        
        print(f"📦 已归档到: {archive_file}")
        
        # 从原文件中删除
        new_lines = []
        skip_lines = set()
        
        for section in sections:
            for i in range(section['start_line'], section['end_line'] + 1):
                skip_lines.add(i)
        
        for i, line in enumerate(lines):
            if i not in skip_lines:
                new_lines.append(line)
        
        # 写回原文件
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        sections = self.parse_memory_sections()
        
        stats = {
            "total": len(sections),
            "by_priority": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
            "with_ttl": 0,
            "without_ttl": 0
        }
        
        for section in sections:
            priority = section['priority']
            stats["by_priority"][priority] += 1
            
            if section.get('ttl'):
                stats["with_ttl"] += 1
            else:
                stats["without_ttl"] += 1
        
        return stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="记忆 TTL 管理器")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # add-markers 命令
    add_parser = subparsers.add_parser("add-markers", help="添加 TTL 标记")
    add_parser.add_argument("--workspace", default=os.path.expanduser("~/.openclaw/workspace"), help="工作区目录")
    
    # check 命令
    check_parser = subparsers.add_parser("check", help="检查过期记忆")
    check_parser.add_argument("--workspace", default=os.path.expanduser("~/.openclaw/workspace"), help="工作区目录")
    
    # clean 命令
    clean_parser = subparsers.add_parser("clean", help="清理过期记忆")
    clean_parser.add_argument("--workspace", default=os.path.expanduser("~/.openclaw/workspace"), help="工作区目录")
    clean_parser.add_argument("--execute", action="store_true", help="执行实际清理（默认为预览模式）")
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="查看统计信息")
    stats_parser.add_argument("--workspace", default=os.path.expanduser("~/.openclaw/workspace"), help="工作区目录")
    
    args = parser.parse_args()
    
    workspace_dir = Path(args.workspace)
    manager = MemoryTTLManager(workspace_dir)
    
    if args.command == "add-markers":
        manager.add_ttl_markers()
    
    elif args.command == "check":
        sections = manager.parse_memory_sections()
        
        if sections:
            print(f"📋 MEMORY.md 章节 ({len(sections)}):\n")
            for section in sections:
                is_expired, reason = manager.check_expiration(section)
                status = "⚠️ 过期" if is_expired else "✅ 有效"
                
                print(f"{status} [{section['priority']}] {section['title']}")
                print(f"     TTL: {section.get('ttl', '未设置')} - {reason}")
                print()
        else:
            print("❌ MEMORY.md 中没有找到章节")
    
    elif args.command == "clean":
        manager.clean_expired(dry_run=not args.execute)
    
    elif args.command == "stats":
        stats = manager.get_stats()
        print("📊 记忆统计:")
        print(f"  总章节数: {stats['total']}")
        print(f"  按优先级:")
        for priority in ["P0", "P1", "P2", "P3"]:
            count = stats['by_priority'][priority]
            print(f"    {priority}: {count}")
        print(f"  有 TTL 标记: {stats['with_ttl']}")
        print(f"  无 TTL 标记: {stats['without_ttl']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
