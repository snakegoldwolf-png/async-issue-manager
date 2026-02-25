#!/usr/bin/env python3
"""
记忆索引系统 - 提供快速检索能力
基于 Hunter 的分析，实现永续 Agent 的第三层记忆架构
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
import hashlib


class MemoryIndexer:
    """记忆索引器 - 构建和维护记忆索引"""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.memory_dir = workspace_dir / "memory"
        self.index_file = self.memory_dir / "index.json"
        
        # 确保目录存在
        self.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def build_index(self) -> Dict:
        """构建完整索引"""
        index = {
            "keywords": {},
            "tags": {},
            "priorities": {},
            "files": {},
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        # 索引 MEMORY.md
        memory_file = self.workspace_dir / "MEMORY.md"
        if memory_file.exists():
            self._index_file(memory_file, index)
        
        # 索引每日日志
        for daily_file in self.memory_dir.glob("*.md"):
            if daily_file.name != "index.json":
                self._index_file(daily_file, index)
        
        return index
    
    def _index_file(self, file_path: Path, index: Dict):
        """索引单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️ 无法读取文件 {file_path}: {e}")
            return
        
        # 文件相对路径
        rel_path = str(file_path.relative_to(self.workspace_dir))
        
        # 文件元数据
        file_hash = hashlib.md5(content.encode()).hexdigest()
        index["files"][rel_path] = {
            "size": len(content),
            "hash": file_hash,
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        # 提取标题和锚点
        sections = self._extract_sections(content, rel_path)
        
        # 提取关键词
        keywords = self._extract_keywords(content)
        for keyword in keywords:
            if keyword not in index["keywords"]:
                index["keywords"][keyword] = []
            index["keywords"][keyword].append(rel_path)
        
        # 提取标签
        tags = self._extract_tags(content)
        for tag in tags:
            if tag not in index["tags"]:
                index["tags"][tag] = []
            index["tags"][tag].append(rel_path)
        
        # 提取优先级
        priorities = self._extract_priorities(content, rel_path)
        for priority, locations in priorities.items():
            if priority not in index["priorities"]:
                index["priorities"][priority] = []
            index["priorities"][priority].extend(locations)
    
    def _extract_sections(self, content: str, file_path: str) -> List[Dict]:
        """提取章节标题和锚点"""
        sections = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 匹配 Markdown 标题
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                
                # 生成锚点
                anchor = self._generate_anchor(title)
                
                sections.append({
                    "level": level,
                    "title": title,
                    "anchor": anchor,
                    "line": i + 1,
                    "location": f"{file_path}#{anchor}"
                })
        
        return sections
    
    def _generate_anchor(self, title: str) -> str:
        """生成 Markdown 锚点"""
        # 移除特殊字符，转小写，空格转连字符
        anchor = re.sub(r'[^\w\s-]', '', title)
        anchor = re.sub(r'\s+', '-', anchor)
        return anchor.lower()
    
    def _extract_keywords(self, content: str) -> Set[str]:
        """提取关键词"""
        keywords = set()
        
        # 常见技术关键词模式
        patterns = [
            r'\b(bug|feature|enhancement|hotfix|critical)\b',
            r'\b(PR|Issue|commit|merge|review)\b',
            r'\b(bounty|Algora|GitHub|Nuclei)\b',
            r'\b(Python|JavaScript|TypeScript|Rust|Go)\b',
            r'\b(API|CLI|SDK|UI|UX)\b',
            r'\b(测试|部署|发布|回滚)\b',
            r'\b(优化|重构|清理|归档)\b',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            keywords.update([m.lower() for m in matches])
        
        return keywords
    
    def _extract_tags(self, content: str) -> Set[str]:
        """提取标签（#tag 格式）"""
        tags = set()
        
        # 匹配 #tag 格式
        matches = re.findall(r'#(\w+)', content)
        tags.update(matches)
        
        return tags
    
    def _extract_priorities(self, content: str, file_path: str) -> Dict[str, List[str]]:
        """提取优先级标记"""
        priorities = {}
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 匹配 [P0], [P1], [P2], [P3]
            match = re.search(r'\[P([0-3])\]', line)
            if match:
                priority = f"P{match.group(1)}"
                
                # 尝试提取标题
                title_match = re.search(r'\[P[0-3]\]\s+(.+)', line)
                title = title_match.group(1).strip() if title_match else f"Line {i+1}"
                
                location = f"{file_path}#L{i+1}"
                
                if priority not in priorities:
                    priorities[priority] = []
                priorities[priority].append({
                    "title": title,
                    "location": location
                })
        
        return priorities
    
    def save_index(self, index: Dict):
        """保存索引到文件"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 索引已保存: {self.index_file}")
    
    def load_index(self) -> Dict:
        """加载索引"""
        if not self.index_file.exists():
            return None
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def search(self, query: str, index: Dict = None) -> List[Dict]:
        """搜索记忆"""
        if index is None:
            index = self.load_index()
            if index is None:
                return []
        
        results = []
        query_lower = query.lower()
        
        # 搜索关键词
        if query_lower in index["keywords"]:
            for file_path in index["keywords"][query_lower]:
                results.append({
                    "type": "keyword",
                    "query": query,
                    "file": file_path,
                    "relevance": 1.0
                })
        
        # 搜索标签
        if query in index["tags"]:
            for file_path in index["tags"][query]:
                results.append({
                    "type": "tag",
                    "query": query,
                    "file": file_path,
                    "relevance": 0.9
                })
        
        # 搜索优先级
        if query.upper() in index["priorities"]:
            for item in index["priorities"][query.upper()]:
                results.append({
                    "type": "priority",
                    "query": query,
                    "title": item["title"],
                    "location": item["location"],
                    "relevance": 0.8
                })
        
        # 按相关度排序
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        return results
    
    def get_stats(self, index: Dict = None) -> Dict:
        """获取索引统计信息"""
        if index is None:
            index = self.load_index()
            if index is None:
                return {}
        
        return {
            "total_files": len(index["files"]),
            "total_keywords": len(index["keywords"]),
            "total_tags": len(index["tags"]),
            "priorities": {
                "P0": len(index["priorities"].get("P0", [])),
                "P1": len(index["priorities"].get("P1", [])),
                "P2": len(index["priorities"].get("P2", [])),
                "P3": len(index["priorities"].get("P3", []))
            },
            "last_updated": index["last_updated"]
        }


def main():
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
    stats_parser.add_argument("--workspace", default=os.path.expanduser("~/.openclaw/workspace"), help="工作区目录")
    
    args = parser.parse_args()
    
    workspace_dir = Path(args.workspace)
    indexer = MemoryIndexer(workspace_dir)
    
    if args.command == "build":
        print("🔨 构建记忆索引...")
        index = indexer.build_index()
        indexer.save_index(index)
        
        stats = indexer.get_stats(index)
        print(f"\n📊 索引统计:")
        print(f"  文件数: {stats['total_files']}")
        print(f"  关键词: {stats['total_keywords']}")
        print(f"  标签: {stats['total_tags']}")
        print(f"  优先级: P0={stats['priorities']['P0']}, P1={stats['priorities']['P1']}, P2={stats['priorities']['P2']}, P3={stats['priorities']['P3']}")
    
    elif args.command == "search":
        results = indexer.search(args.query)
        
        if results:
            print(f"🔍 搜索结果 ({len(results)}):\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. [{result['type']}] {result.get('file', result.get('location', 'N/A'))}")
                if 'title' in result:
                    print(f"   标题: {result['title']}")
                print(f"   相关度: {result['relevance']:.1%}\n")
        else:
            print(f"❌ 未找到相关结果: {args.query}")
    
    elif args.command == "stats":
        stats = indexer.get_stats()
        if stats:
            print("📊 索引统计:")
            print(f"  文件数: {stats['total_files']}")
            print(f"  关键词: {stats['total_keywords']}")
            print(f"  标签: {stats['total_tags']}")
            print(f"  优先级: P0={stats['priorities']['P0']}, P1={stats['priorities']['P1']}, P2={stats['priorities']['P2']}, P3={stats['priorities']['P3']}")
            print(f"  最后更新: {stats['last_updated']}")
        else:
            print("❌ 索引不存在，请先运行 build 命令")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
