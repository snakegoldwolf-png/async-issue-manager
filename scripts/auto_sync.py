#!/usr/bin/env python3
"""
自动同步模块 - 让同步「自然发生」

功能：
1. 任务完成自动同步 - 检测完成关键词，自动同步到 Obsidian
2. Issue 关闭自动同步 - 关闭时同步完整内容
3. 每日自动汇总 - 同步各 Agent 日报
4. 同步统计 - 显示知识贡献数量

用法：
  python3 auto_sync.py detect "任务完成！已实现XXX功能" --agent dev
  python3 auto_sync.py issue-close 10
  python3 auto_sync.py daily-summary
  python3 auto_sync.py stats --agent dev
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 路径配置
BASE_DIR = Path.home() / ".openclaw"
SHARED_DIR = BASE_DIR / "shared"
ISSUE_MANAGER_DIR = SHARED_DIR / "async-issue-manager"
OBSIDIAN_DIR = SHARED_DIR / "obsidian-vault"
STATS_FILE = SHARED_DIR / "sync-stats.json"

# 导入同步模块
sys.path.insert(0, str(OBSIDIAN_DIR / "scripts"))
sys.path.insert(0, str(ISSUE_MANAGER_DIR / "scripts"))

# 完成关键词
COMPLETION_KEYWORDS = [
    "完成", "已完成", "Done", "done", "✅", "搞定", 
    "OK", "ok", "完毕", "结束", "finished", "Finished",
    "任务完成", "Issue 完成", "实现完成"
]

# Agent 列表
AGENTS = [
    "leader", "anna", "debugger", "dev", "filer", 
    "haire", "hunter", "memo", "muse", "prad", 
    "webby", "xiaohong"
]


def load_stats():
    """加载同步统计"""
    if STATS_FILE.exists():
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "by_agent": {},
        "by_date": {},
        "total": 0,
        "last_updated": None
    }


def save_stats(stats):
    """保存同步统计"""
    stats["last_updated"] = datetime.now().isoformat()
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def update_stats(agent: str, sync_type: str = "knowledge"):
    """更新同步统计"""
    stats = load_stats()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 更新 agent 统计
    if agent not in stats["by_agent"]:
        stats["by_agent"][agent] = {"total": 0, "by_type": {}}
    stats["by_agent"][agent]["total"] += 1
    stats["by_agent"][agent]["by_type"][sync_type] = \
        stats["by_agent"][agent]["by_type"].get(sync_type, 0) + 1
    
    # 更新日期统计
    if today not in stats["by_date"]:
        stats["by_date"][today] = {"total": 0, "by_agent": {}}
    stats["by_date"][today]["total"] += 1
    stats["by_date"][today]["by_agent"][agent] = \
        stats["by_date"][today]["by_agent"].get(agent, 0) + 1
    
    # 更新总计
    stats["total"] += 1
    
    save_stats(stats)
    return stats


def get_agent_stats(agent: str):
    """获取 Agent 的同步统计"""
    stats = load_stats()
    today = datetime.now().strftime("%Y-%m-%d")
    
    agent_stats = stats["by_agent"].get(agent, {"total": 0})
    today_stats = stats["by_date"].get(today, {"by_agent": {}})
    
    # 计算本周统计
    week_total = 0
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        if date in stats["by_date"]:
            week_total += stats["by_date"][date]["by_agent"].get(agent, 0)
    
    # 计算排名
    all_agents = [(a, s["total"]) for a, s in stats["by_agent"].items()]
    all_agents.sort(key=lambda x: x[1], reverse=True)
    rank = next((i+1 for i, (a, _) in enumerate(all_agents) if a == agent), len(all_agents)+1)
    
    return {
        "today": today_stats["by_agent"].get(agent, 0),
        "week": week_total,
        "total": agent_stats["total"],
        "rank": rank,
        "total_agents": len(all_agents)
    }


def display_stats(agent: str):
    """显示同步统计"""
    s = get_agent_stats(agent)
    
    # 排名 emoji
    rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(s["rank"], f"#{s['rank']}")
    
    print(f"""
✅ 同步成功！

📊 你的知识贡献：
  - 今日同步：{s['today']} 条
  - 本周同步：{s['week']} 条
  - 总计贡献：{s['total']} 条
  - 团队排名：{rank_emoji} / {s['total_agents']} 人

💡 继续加油，让知识沉淀成为习惯！
""")


def detect_completion(message: str) -> bool:
    """检测消息是否包含完成关键词"""
    return any(kw in message for kw in COMPLETION_KEYWORDS)


def extract_summary(message: str) -> str:
    """从消息中提取摘要"""
    # 移除常见的前缀
    prefixes = ["✅", "完成！", "已完成！", "Done!", "任务完成！"]
    summary = message
    for prefix in prefixes:
        if summary.startswith(prefix):
            summary = summary[len(prefix):].strip()
    
    # 截取前 500 字符
    if len(summary) > 500:
        summary = summary[:500] + "..."
    
    return summary


def sync_to_obsidian(content: str, content_type: str, agent: str, title: str = None):
    """同步到 Obsidian"""
    try:
        from sync_to_obsidian import sync_content
        
        result = sync_content(
            content=content,
            content_type=content_type,
            agent=agent if agent != "leader" else "dev",  # leader 映射到 dev
            title=title,
            tags=["自动同步", agent, datetime.now().strftime("%Y-%m-%d")]
        )
        
        if result.get("status") == "success":
            # 更新统计
            update_stats(agent, content_type)
            return True, result.get("path", "unknown")
        else:
            return False, str(result)
    except Exception as e:
        return False, str(e)


def auto_sync_completion(message: str, agent: str):
    """任务完成自动同步"""
    if not detect_completion(message):
        print("❌ 未检测到完成关键词，跳过同步")
        return False
    
    summary = extract_summary(message)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    content = f"""# 任务完成记录

**时间**: {timestamp}
**Agent**: {agent}

## 完成内容

{summary}

---
*自动同步 by auto_sync.py*
"""
    
    success, path = sync_to_obsidian(
        content=content,
        content_type="work",
        agent=agent,
        title=f"{timestamp[:10]}-任务完成"
    )
    
    if success:
        display_stats(agent)
        print(f"📁 文件位置: {path}")
        return True
    else:
        print(f"❌ 同步失败: {path}")
        return False


def auto_sync_issue_close(issue_id: int):
    """Issue 关闭自动同步"""
    try:
        from manager import IssueManager
        
        manager = IssueManager()
        issue = manager.get(issue_id)
        
        if not issue:
            print(f"❌ Issue #{issue_id} 不存在")
            return False
        
        # 读取进度记录
        progress_file = ISSUE_MANAGER_DIR / ".issues" / "progress.jsonl"
        progress_history = []
        
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get("issue_id") == issue_id:
                            progress_history.append(record)
                    except:
                        continue
        
        # 构建内容
        content = f"""# Issue #{issue_id}: {issue.get('title', '')}

## 基本信息

- **状态**: {issue.get('status', '')}
- **优先级**: {issue.get('priority', '')}
- **负责人**: {issue.get('assignee', '')}
- **创建时间**: {issue.get('created_at', '')}
- **关闭时间**: {issue.get('closed_at', datetime.now().isoformat())}

## 描述

{issue.get('content', issue.get('body', ''))}

## 进度记录

"""
        for p in progress_history:
            content += f"### {p.get('timestamp', '')}\n\n{p.get('progress', '')}\n\n"
        
        if issue.get('resolution'):
            content += f"""## 解决方案

{issue.get('resolution')}
"""
        
        content += "\n---\n*自动同步 by auto_sync.py*\n"
        
        # 同步
        agent = issue.get('assignee', 'dev')
        success, path = sync_to_obsidian(
            content=content,
            content_type="task_closed",
            agent=agent,
            title=f"Issue-{issue_id:03d}"
        )
        
        if success:
            display_stats(agent)
            print(f"📁 文件位置: {path}")
            return True
        else:
            print(f"❌ 同步失败: {path}")
            return False
            
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        return False


def auto_sync_daily_summary():
    """每日自动汇总同步"""
    today = datetime.now().strftime("%Y-%m-%d")
    synced = 0
    
    print(f"🔄 开始每日汇总同步 ({today})...\n")
    
    for agent in AGENTS:
        # 确定 workspace 路径
        if agent == "leader":
            workspace = BASE_DIR / "workspace"
        else:
            workspace = BASE_DIR / f"workspace-{agent}"
        
        # 读取今天的日志
        log_file = workspace / "memory" / f"{today}.md"
        
        if not log_file.exists():
            continue
        
        try:
            content = log_file.read_text(encoding='utf-8')
            
            if len(content.strip()) < 50:  # 内容太少，跳过
                continue
            
            success, path = sync_to_obsidian(
                content=content,
                content_type="diary",
                agent=agent,
                title=f"{today}"
            )
            
            if success:
                print(f"  ✅ {agent}: 同步成功")
                synced += 1
            else:
                print(f"  ⚠️ {agent}: {path}")
                
        except Exception as e:
            print(f"  ❌ {agent}: {e}")
    
    print(f"\n📊 每日汇总完成: {synced} 个 Agent 的日报已同步")
    return synced


def show_leaderboard():
    """显示知识贡献榜"""
    stats = load_stats()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 今日排行
    today_stats = stats["by_date"].get(today, {"by_agent": {}})
    today_ranking = sorted(
        today_stats["by_agent"].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # 总排行
    total_ranking = sorted(
        [(a, s["total"]) for a, s in stats["by_agent"].items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    print(f"""
📊 知识贡献榜 ({today})

🏆 今日排行:
""")
    
    medals = ["🥇", "🥈", "🥉"]
    for i, (agent, count) in enumerate(today_ranking[:5]):
        medal = medals[i] if i < 3 else f"#{i+1}"
        print(f"  {medal} {agent} - {count} 条")
    
    if not today_ranking:
        print("  (今日暂无贡献)")
    
    print(f"""
📈 总排行:
""")
    
    for i, (agent, count) in enumerate(total_ranking[:5]):
        medal = medals[i] if i < 3 else f"#{i+1}"
        print(f"  {medal} {agent} - {count} 条")
    
    print(f"\n💡 总计: {stats['total']} 条知识已沉淀")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="自动同步模块")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # detect 命令
    detect_parser = subparsers.add_parser("detect", help="检测并同步任务完成消息")
    detect_parser.add_argument("message", help="消息内容")
    detect_parser.add_argument("--agent", "-a", required=True, help="Agent 名称")
    
    # issue-close 命令
    issue_parser = subparsers.add_parser("issue-close", help="Issue 关闭同步")
    issue_parser.add_argument("issue_id", type=int, help="Issue ID")
    
    # daily-summary 命令
    subparsers.add_parser("daily-summary", help="每日汇总同步")
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="显示同步统计")
    stats_parser.add_argument("--agent", "-a", help="Agent 名称")
    
    # leaderboard 命令
    subparsers.add_parser("leaderboard", help="显示知识贡献榜")
    
    args = parser.parse_args()
    
    if args.command == "detect":
        auto_sync_completion(args.message, args.agent)
    elif args.command == "issue-close":
        auto_sync_issue_close(args.issue_id)
    elif args.command == "daily-summary":
        auto_sync_daily_summary()
    elif args.command == "stats":
        if args.agent:
            display_stats(args.agent)
        else:
            show_leaderboard()
    elif args.command == "leaderboard":
        show_leaderboard()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
