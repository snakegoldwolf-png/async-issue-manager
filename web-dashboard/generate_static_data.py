#!/usr/bin/env python3
"""
生成静态 JSON 数据文件，用于 Cloudflare Pages 部署
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
ISSUES_DIR = ROOT_DIR / ".issues"
OUTPUT_DIR = Path(__file__).parent / "data"

def parse_issue_file(file_path):
    """解析 Issue Markdown 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 frontmatter
    if not content.startswith('---'):
        return None
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None
    
    frontmatter = parts[1].strip()
    body = parts[2].strip()
    
    # 解析 frontmatter
    issue = {}
    current_key = None
    current_list = []
    
    for line in frontmatter.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('- '):
            # 列表项
            current_list.append(line[2:].strip())
        elif ':' in line:
            # 保存之前的列表
            if current_key and current_list:
                issue[current_key] = current_list
                current_list = []
            
            # 新的键值对
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value:
                issue[key] = value
                current_key = None
            else:
                current_key = key
    
    # 保存最后的列表
    if current_key and current_list:
        issue[current_key] = current_list
    
    # 解析 body 中的特殊部分
    sections = {}
    current_section = None
    section_content = []
    
    # 保存完整的 body 内容
    full_body = body
    
    for line in body.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(section_content).strip()
            current_section = line[3:].strip()
            section_content = []
        else:
            section_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(section_content).strip()
    
    # 提取进度记录
    progress_history = []
    if '进度记录' in sections:
        progress_text = sections['进度记录']
        for block in progress_text.split('\n\n'):
            if block.strip().startswith('###'):
                lines = block.strip().split('\n')
                header = lines[0].replace('###', '').strip()
                content = '\n'.join(lines[1:]).strip()
                
                # 解析时间戳和 agent
                if ' - ' in header:
                    timestamp_str, agent = header.split(' - ', 1)
                    progress_history.append({
                        'timestamp': timestamp_str.strip(),
                        'agent': agent.strip(),
                        'progress': content
                    })
    
    # 提取交付物
    deliverables = []
    if '交付物' in sections:
        deliverable_text = sections['交付物']
        for line in deliverable_text.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                parts = line[2:].split(':', 1)
                if len(parts) == 2:
                    deliverables.append({
                        'file': parts[0].strip(),
                        'description': parts[1].strip()
                    })
    
    # 构建完整的 issue 对象
    result = {
        'id': int(issue.get('id', 0)),
        'title': issue.get('title', ''),
        'status': issue.get('status', 'open'),
        'priority': issue.get('priority', 'P2'),
        'labels': issue.get('labels', []),
        'assignee': issue.get('assignee'),
        'created_at': issue.get('created_at'),
        'updated_at': issue.get('updated_at'),
        'assigned_at': issue.get('assigned_at'),
        'closed_at': issue.get('closed_at'),
        'file': str(file_path.relative_to(ROOT_DIR)),
        'body': full_body,  # 使用完整的 body 内容
        'progress_history': progress_history,
        'deliverables': deliverables,
        'resolution': sections.get('解决方案')
    }
    
    return result

def collect_all_issues():
    """收集所有 Issue"""
    issues = []
    
    for status_dir in ['open', 'in-progress', 'closed']:
        status_path = ISSUES_DIR / status_dir
        if not status_path.exists():
            continue
        
        for file_path in status_path.glob('*.md'):
            issue = parse_issue_file(file_path)
            if issue:
                issues.append(issue)
    
    return sorted(issues, key=lambda x: x['id'])

def generate_stats(issues):
    """生成统计信息"""
    stats = {
        'total': len(issues),
        'by_status': defaultdict(int),
        'by_priority': defaultdict(int),
        'by_assignee': defaultdict(int),
        'by_label': defaultdict(int)
    }
    
    for issue in issues:
        stats['by_status'][issue['status']] += 1
        stats['by_priority'][issue['priority']] += 1
        
        if issue['assignee']:
            stats['by_assignee'][issue['assignee']] += 1
        
        for label in issue['labels']:
            stats['by_label'][label] += 1
    
    # 转换 defaultdict 为普通 dict
    return {
        'total': stats['total'],
        'by_status': dict(stats['by_status']),
        'by_priority': dict(stats['by_priority']),
        'by_assignee': dict(stats['by_assignee']),
        'by_label': dict(stats['by_label'])
    }

def generate_agents_info(issues):
    """生成 Agent 信息"""
    agents = defaultdict(lambda: {
        'name': '',
        'total': 0,
        'open': 0,
        'in_progress': 0,
        'closed': 0
    })
    
    for issue in issues:
        if not issue['assignee']:
            continue
        
        agent_name = issue['assignee']
        agents[agent_name]['name'] = agent_name
        agents[agent_name]['total'] += 1
        
        if issue['status'] == 'open':
            agents[agent_name]['open'] += 1
        elif issue['status'] == 'in-progress':
            agents[agent_name]['in_progress'] += 1
        elif issue['status'] == 'closed':
            agents[agent_name]['closed'] += 1
    
    return {
        'total': len(agents),
        'agents': sorted(agents.values(), key=lambda x: x['total'], reverse=True)
    }

def load_progress_history():
    """从 progress.jsonl 加载进度记录"""
    progress_file = ISSUES_DIR / 'progress.jsonl'
    progress_by_issue = defaultdict(list)
    
    if progress_file.exists():
        with open(progress_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    issue_id = record.get('issue_id')
                    if issue_id:
                        progress_by_issue[issue_id].append({
                            'timestamp': record.get('timestamp', ''),
                            'agent': record.get('agent', ''),
                            'progress': record.get('progress', '')
                        })
                except json.JSONDecodeError:
                    continue
    
    return progress_by_issue

def load_deliverables():
    """从 deliverables/index.json 加载交付物"""
    deliverables_file = ISSUES_DIR / 'deliverables' / 'index.json'
    deliverables_by_issue = defaultdict(list)
    
    if deliverables_file.exists():
        with open(deliverables_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for item in data.get('deliverables', []):
                    issue_id = item.get('issue_id')
                    if issue_id:
                        deliverables_by_issue[issue_id].append({
                            'file': item.get('file', ''),
                            'description': item.get('description', ''),
                            'added_at': item.get('added_at', '')
                        })
            except json.JSONDecodeError:
                pass
    
    return deliverables_by_issue

def main():
    """主函数"""
    print("🔄 开始生成静态数据...")
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 收集所有 Issue
    print("📋 收集 Issues...")
    issues = collect_all_issues()
    print(f"   找到 {len(issues)} 个 Issues")
    
    # 加载进度记录和交付物
    print("📝 加载进度记录...")
    progress_by_issue = load_progress_history()
    
    print("📦 加载交付物...")
    deliverables_by_issue = load_deliverables()
    
    # 合并进度记录和交付物到 Issue
    for issue in issues:
        issue_id = issue['id']
        if issue_id in progress_by_issue:
            issue['progress_history'] = progress_by_issue[issue_id]
        if issue_id in deliverables_by_issue:
            issue['deliverables'] = deliverables_by_issue[issue_id]
    
    # 生成统计信息
    print("📊 生成统计信息...")
    stats = generate_stats(issues)
    
    # 生成 Agent 信息
    print("👥 生成 Agent 信息...")
    agents = generate_agents_info(issues)
    
    # 写入文件
    print("💾 写入数据文件...")
    
    # issues.json - 所有 Issue 列表
    with open(OUTPUT_DIR / 'issues.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(issues),
            'issues': issues,
            'generated_at': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    print(f"   ✓ issues.json ({len(issues)} issues)")
    
    # stats.json - 统计信息
    with open(OUTPUT_DIR / 'stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"   ✓ stats.json")
    
    # agents.json - Agent 信息
    with open(OUTPUT_DIR / 'agents.json', 'w', encoding='utf-8') as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)
    print(f"   ✓ agents.json ({agents['total']} agents)")
    
    # 为每个 Issue 生成单独的文件（可选，用于详情页）
    issues_detail_dir = OUTPUT_DIR / 'issues'
    issues_detail_dir.mkdir(exist_ok=True)
    
    for issue in issues:
        issue_file = issues_detail_dir / f"{issue['id']}.json"
        with open(issue_file, 'w', encoding='utf-8') as f:
            json.dump(issue, f, ensure_ascii=False, indent=2)
    print(f"   ✓ issues/*.json ({len(issues)} files)")
    
    # 生成元数据
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'total_issues': len(issues),
        'version': '1.0.0'
    }
    with open(OUTPUT_DIR / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"   ✓ metadata.json")
    
    print("\n✅ 静态数据生成完成！")
    print(f"   输出目录: {OUTPUT_DIR}")
    print(f"   总计: {len(issues)} issues, {agents['total']} agents")

if __name__ == '__main__':
    main()
