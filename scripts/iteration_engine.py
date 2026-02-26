#!/usr/bin/env python3
"""
自动迭代引擎 - 后台自动检测重复问题并执行迭代

功能：
- scan: 扫描所有 Agent 的记忆，检测重复问题
- analyze: 分析问题原因
- iterate: 执行迭代（低风险自动，高风险记录）
- report: 生成改进报告

用法：
  python3 iteration_engine.py scan      # 扫描检测重复问题
  python3 iteration_engine.py iterate   # 执行自动迭代
  python3 iteration_engine.py report    # 生成改进报告
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from collections import defaultdict


# 所有 Agent 的 workspace
WORKSPACES = [
    "workspace",  # Leader
    "workspace-anna",
    "workspace-debugger",
    "workspace-dev",
    "workspace-filer",
    "workspace-haire",
    "workspace-hunter",
    "workspace-memo",
    "workspace-muse",
    "workspace-prad",
    "workspace-webby",
    "workspace-xiaohong",
]

# 问题关键词模式
PROBLEM_PATTERNS = [
    r'问题[：:].+',
    r'错误[：:].+',
    r'失败[：:].+',
    r'bug[：:].+',
    r'issue[：:].+',
    r'❌.+',
    r'⚠️.+',
    r'报错.+',
    r'异常.+',
    r'无法.+',
    r'不能.+',
    r'卡住.+',
    r'超时.+',
    r'丢失.+',
]

# 低风险改动（可以自动执行）
LOW_RISK_ACTIONS = [
    "write_memory",      # 写入 MEMORY.md
    "create_iteration",  # 创建迭代记录
    "update_index",      # 更新索引
    "add_log",           # 添加日志
]

# 高风险改动（只记录，不执行）
HIGH_RISK_ACTIONS = [
    "modify_agents_md",  # 修改 AGENTS.md
    "modify_script",     # 修改脚本
    "modify_config",     # 修改配置
    "modify_soul",       # 修改 SOUL.md
]


class IterationEngine:
    """自动迭代引擎"""
    
    def __init__(self):
        self.base_dir = Path.home() / ".openclaw"
        self.shared_dir = self.base_dir / "shared" / "async-issue-manager"
        self.iterations_dir = self.shared_dir / "iterations"
        self.pending_file = self.shared_dir / "pending-improvements.md"
        self.report_file = self.shared_dir / "iteration-report.md"
        
        # 确保目录存在
        self.iterations_dir.mkdir(parents=True, exist_ok=True)
    
    def scan(self) -> List[Dict]:
        """扫描所有 Agent 的记忆，检测重复问题"""
        print("🔍 开始扫描所有 Agent 的记忆...")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        
        all_problems = []
        
        for workspace_name in WORKSPACES:
            workspace_path = self.base_dir / workspace_name
            if not workspace_path.exists():
                continue
            
            problems = self._scan_workspace(workspace_path, workspace_name)
            all_problems.extend(problems)
        
        # 检测重复问题
        repeated = self._detect_repetition(all_problems)
        
        print(f"\n📊 扫描结果:")
        print(f"  - 扫描 Agent 数: {len(WORKSPACES)}")
        print(f"  - 发现问题数: {len(all_problems)}")
        print(f"  - 重复问题数: {len(repeated)}")
        
        if repeated:
            print(f"\n⚠️ 发现 {len(repeated)} 个重复问题需要迭代:")
            for i, problem in enumerate(repeated, 1):
                print(f"  {i}. {problem['signature'][:50]}... (出现 {problem['count']} 次)")
        else:
            print(f"\n✅ 没有发现需要迭代的重复问题")
        
        return repeated
    
    def _scan_workspace(self, workspace_path: Path, workspace_name: str) -> List[Dict]:
        """扫描单个 workspace"""
        problems = []
        
        # 扫描 MEMORY.md
        memory_file = workspace_path / "MEMORY.md"
        if memory_file.exists():
            problems.extend(self._extract_problems(memory_file, workspace_name))
        
        # 扫描 memory/*.md
        memory_dir = workspace_path / "memory"
        if memory_dir.exists():
            for md_file in memory_dir.glob("*.md"):
                problems.extend(self._extract_problems(md_file, workspace_name))
        
        return problems
    
    def _extract_problems(self, file_path: Path, workspace_name: str) -> List[Dict]:
        """从文件中提取问题"""
        problems = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return problems
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in PROBLEM_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    # 生成问题签名
                    signature = self._generate_signature(line)
                    
                    problems.append({
                        'signature': signature,
                        'original': line.strip(),
                        'file': str(file_path),
                        'line': i + 1,
                        'workspace': workspace_name,
                        'timestamp': datetime.now().isoformat()
                    })
                    break
        
        return problems
    
    def _generate_signature(self, text: str) -> str:
        """生成问题签名（用于检测重复）"""
        # 移除特殊字符和数字
        cleaned = re.sub(r'[^\w\u4e00-\u9fff]', ' ', text)
        cleaned = re.sub(r'\d+', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
        
        # 提取关键词
        keywords = sorted(set(cleaned.split()))
        
        return ' '.join(keywords[:10])  # 取前 10 个关键词
    
    def _detect_repetition(self, problems: List[Dict]) -> List[Dict]:
        """检测重复问题"""
        signature_count = defaultdict(list)
        
        for problem in problems:
            signature_count[problem['signature']].append(problem)
        
        # 找出出现 >= 2 次的问题
        repeated = []
        for signature, occurrences in signature_count.items():
            if len(occurrences) >= 2:
                repeated.append({
                    'signature': signature,
                    'count': len(occurrences),
                    'occurrences': occurrences,
                    'first_seen': min(o['timestamp'] for o in occurrences),
                    'last_seen': max(o['timestamp'] for o in occurrences),
                })
        
        # 按出现次数排序
        repeated.sort(key=lambda x: x['count'], reverse=True)
        
        return repeated
    
    def iterate(self, problems: List[Dict] = None) -> Dict:
        """执行自动迭代"""
        if problems is None:
            problems = self.scan()
        
        if not problems:
            print("\n✅ 没有需要迭代的问题")
            return {'status': 'no_action', 'iterations': 0}
        
        print(f"\n🔄 开始执行迭代...")
        
        iterations_done = 0
        pending_improvements = []
        
        for problem in problems:
            result = self._execute_iteration(problem)
            
            if result['action'] == 'executed':
                iterations_done += 1
            elif result['action'] == 'pending':
                pending_improvements.append(result)
        
        # 保存待审核的高风险改进
        if pending_improvements:
            self._save_pending_improvements(pending_improvements)
        
        print(f"\n📊 迭代结果:")
        print(f"  - 自动执行: {iterations_done} 个")
        print(f"  - 待审核: {len(pending_improvements)} 个")
        
        return {
            'status': 'completed',
            'iterations': iterations_done,
            'pending': len(pending_improvements)
        }
    
    def _execute_iteration(self, problem: Dict) -> Dict:
        """执行单个迭代"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        
        # 分析问题
        analysis = self._analyze_problem(problem)
        
        # 设计方案
        solution = self._design_solution(problem, analysis)
        
        # 判断风险等级
        if solution['risk'] == 'low':
            # 低风险：自动执行
            self._execute_low_risk(problem, analysis, solution, timestamp)
            return {'action': 'executed', 'problem': problem, 'solution': solution}
        else:
            # 高风险：只记录
            return {'action': 'pending', 'problem': problem, 'solution': solution}
    
    def _analyze_problem(self, problem: Dict) -> Dict:
        """分析问题原因"""
        return {
            'signature': problem['signature'],
            'frequency': problem['count'],
            'affected_workspaces': list(set(o['workspace'] for o in problem['occurrences'])),
            'pattern': 'repeated_issue',
            'root_cause': f"问题 '{problem['signature'][:30]}...' 在多个地方重复出现",
        }
    
    def _design_solution(self, problem: Dict, analysis: Dict) -> Dict:
        """设计解决方案"""
        # 默认低风险方案：记录到 MEMORY.md
        return {
            'risk': 'low',
            'action': 'write_memory',
            'description': f"将问题 '{problem['signature'][:30]}...' 记录到 MEMORY.md，防止再次发生",
            'content': f"""## [P2] 重复问题检测 - {problem['signature'][:30]}...
<!-- TTL: 30d -->

**检测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**出现次数**: {problem['count']} 次
**影响范围**: {', '.join(analysis['affected_workspaces'])}

**问题描述**:
{problem['occurrences'][0]['original']}

**根本原因**:
{analysis['root_cause']}

**建议**:
- 注意避免此类问题重复发生
- 如果问题持续出现，考虑添加自动化检测
"""
        }
    
    def _execute_low_risk(self, problem: Dict, analysis: Dict, solution: Dict, timestamp: str):
        """执行低风险改动"""
        # 1. 创建迭代记录
        iteration_file = self.iterations_dir / f"{timestamp}.md"
        iteration_content = f"""# 迭代记录 - {timestamp}

## 元数据
- ID: {timestamp}
- 类型: 自动迭代
- 风险等级: 低
- 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 问题
- 签名: {problem['signature']}
- 出现次数: {problem['count']}
- 影响范围: {', '.join(analysis['affected_workspaces'])}

## 分析
{analysis['root_cause']}

## 方案
{solution['description']}

## 执行
- 动作: {solution['action']}
- 状态: ✅ 已执行

## 写入内容
```markdown
{solution['content']}
```
"""
        iteration_file.write_text(iteration_content, encoding='utf-8')
        print(f"  ✅ 创建迭代记录: {iteration_file.name}")
        
        # 2. 写入共享 MEMORY.md（而不是单个 Agent 的）
        shared_memory = self.shared_dir / "ITERATION_MEMORY.md"
        
        if shared_memory.exists():
            existing = shared_memory.read_text(encoding='utf-8')
        else:
            existing = "# 自动迭代记忆\n\n> 由自动迭代引擎生成的问题记录和改进建议。\n\n---\n\n"
        
        new_content = existing + "\n" + solution['content'] + "\n---\n"
        shared_memory.write_text(new_content, encoding='utf-8')
        print(f"  ✅ 写入迭代记忆: ITERATION_MEMORY.md")
        
        # 3. 同步到 Obsidian Vault
        try:
            import sys
            obsidian_scripts = str(Path.home() / ".openclaw" / "shared" / "obsidian-vault" / "scripts")
            if obsidian_scripts not in sys.path:
                sys.path.insert(0, obsidian_scripts)
            from sync_to_obsidian import sync_content
            
            # 同步迭代记录到 Obsidian
            result = sync_content(
                content=iteration_content,
                content_type="knowledge",
                agent="system",
                title=f"迭代记录-{timestamp}",
                filename=f"iteration-{timestamp}.md",
                tags=["迭代", "自动生成", "系统优化"]
            )
            
            if result.get('status') == 'success':
                print(f"  ✅ 同步到 Obsidian: {result.get('path', 'unknown')}")
            else:
                print(f"  ⚠️ Obsidian 同步返回异常: {result}")
        except ImportError as e:
            print(f"  ⚠️ Obsidian 同步模块未找到: {e}")
        except Exception as e:
            print(f"  ⚠️ Obsidian 同步失败: {e}")
    
    def _save_pending_improvements(self, improvements: List[Dict]):
        """保存待审核的高风险改进"""
        content = f"""# 待审核的改进建议

> 由自动迭代引擎生成，需要人工审核后执行。
> 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
        
        for i, imp in enumerate(improvements, 1):
            content += f"""## {i}. {imp['problem']['signature'][:50]}...

**风险等级**: 高
**出现次数**: {imp['problem']['count']}
**建议方案**: {imp['solution']['description']}

**操作**: [ ] 执行  [ ] 忽略

---

"""
        
        self.pending_file.write_text(content, encoding='utf-8')
        print(f"  📝 保存待审核改进: pending-improvements.md")
    
    def report(self) -> str:
        """生成改进报告"""
        print("📊 生成改进报告...")
        
        # 统计迭代记录
        iterations = list(self.iterations_dir.glob("*.md"))
        
        # 读取待审核改进
        pending_count = 0
        if self.pending_file.exists():
            pending_content = self.pending_file.read_text(encoding='utf-8')
            pending_count = pending_content.count('## ')
        
        report = f"""# 自动迭代报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计

- 总迭代次数: {len(iterations)}
- 待审核改进: {pending_count}

## 最近迭代

"""
        
        # 列出最近 10 个迭代
        recent = sorted(iterations, reverse=True)[:10]
        for it in recent:
            report += f"- {it.name}\n"
        
        self.report_file.write_text(report, encoding='utf-8')
        print(f"✅ 报告已保存: {self.report_file}")
        
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="自动迭代引擎")
    parser.add_argument("command", choices=["scan", "iterate", "report"], help="命令")
    
    args = parser.parse_args()
    
    engine = IterationEngine()
    
    if args.command == "scan":
        engine.scan()
    elif args.command == "iterate":
        engine.iterate()
    elif args.command == "report":
        engine.report()


if __name__ == "__main__":
    main()
