#!/usr/bin/env python3
"""
一键沉淀脚本 - 快速完成任务后的所有沉淀动作

用法:
  python3 quick_sync.py --issue 10 --summary "完成说明" --learnings "经验教训"
  python3 quick_sync.py --issue 10 --summary "完成说明" --file /path/to/deliverable.md
  python3 quick_sync.py --daily --agent dev --summary "今日工作总结"
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 路径配置
BASE_DIR = Path.home() / ".openclaw"
SHARED_DIR = BASE_DIR / "shared"
ISSUE_MANAGER_DIR = SHARED_DIR / "async-issue-manager"
OBSIDIAN_DIR = SHARED_DIR / "obsidian-vault"
DESKTOP_ISSUES_DIR = Path.home() / "Desktop" / "Issues"

# 导入其他模块
sys.path.insert(0, str(ISSUE_MANAGER_DIR / "scripts"))
sys.path.insert(0, str(OBSIDIAN_DIR / "scripts"))


def update_issue_progress(issue_id: int, summary: str, agent: str = None):
    """更新 Issue 进度"""
    try:
        from sync_progress import add_progress
        add_progress(issue_id, summary, agent)
        print(f"✅ Issue #{issue_id} 进度已更新")
        return True
    except Exception as e:
        print(f"⚠️ 更新 Issue 进度失败: {e}")
        # 尝试直接写入 progress.jsonl
        try:
            progress_file = ISSUE_MANAGER_DIR / ".issues" / "progress.jsonl"
            record = {
                "issue_id": issue_id,
                "timestamp": datetime.now().isoformat(),
                "progress": summary,
                "agent": agent or ""
            }
            with open(progress_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"✅ Issue #{issue_id} 进度已更新（直接写入）")
            return True
        except Exception as e2:
            print(f"❌ 更新 Issue 进度失败: {e2}")
            return False


def sync_to_obsidian(content: str, content_type: str, agent: str, title: str = None):
    """同步到 Obsidian"""
    try:
        from sync_to_obsidian import sync_content
        result = sync_content(
            content=content,
            content_type=content_type,
            agent=agent,
            title=title,
            tags=["自动同步", agent]
        )
        if result.get("status") == "success":
            print(f"✅ 已同步到 Obsidian: {result.get('path', 'unknown')}")
            return True
        else:
            print(f"⚠️ Obsidian 同步返回异常: {result}")
            return False
    except Exception as e:
        print(f"⚠️ Obsidian 同步失败: {e}")
        return False


def update_memory(agent: str, content: str):
    """更新 Agent 的 MEMORY.md"""
    try:
        # 确定 workspace 路径
        if agent == "leader":
            workspace = BASE_DIR / "workspace"
        else:
            workspace = BASE_DIR / f"workspace-{agent}"
        
        memory_file = workspace / "MEMORY.md"
        
        if not memory_file.exists():
            print(f"⚠️ MEMORY.md 不存在: {memory_file}")
            return False
        
        # 读取现有内容
        existing = memory_file.read_text(encoding="utf-8")
        
        # 添加新内容
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_entry = f"\n\n## [{timestamp}] 经验沉淀\n\n{content}\n"
        
        # 写入
        memory_file.write_text(existing + new_entry, encoding="utf-8")
        print(f"✅ MEMORY.md 已更新: {memory_file}")
        return True
    except Exception as e:
        print(f"⚠️ 更新 MEMORY.md 失败: {e}")
        return False


def add_deliverable(issue_id: int, file_path: str, description: str = None):
    """添加交付物"""
    try:
        from deliverable import add_deliverable as _add
        _add(issue_id, file_path, description)
        print(f"✅ 交付物已添加: {file_path}")
        return True
    except Exception as e:
        print(f"⚠️ 添加交付物失败: {e}")
        return False


def copy_to_desktop_workspace(issue_id: int, file_path: str):
    """复制文件到桌面工作空间"""
    try:
        import shutil
        
        # 查找 Issue 的工作空间
        for dir_name in os.listdir(DESKTOP_ISSUES_DIR):
            if dir_name.startswith(f"#{issue_id:03d}-"):
                workspace = DESKTOP_ISSUES_DIR / dir_name
                dest = workspace / Path(file_path).name
                shutil.copy2(file_path, dest)
                print(f"✅ 已复制到桌面工作空间: {dest}")
                return True
        
        print(f"⚠️ 未找到 Issue #{issue_id} 的桌面工作空间")
        return False
    except Exception as e:
        print(f"⚠️ 复制到桌面工作空间失败: {e}")
        return False


def quick_sync_issue(issue_id: int, summary: str, learnings: str = None, 
                     file_path: str = None, agent: str = None):
    """一键同步 Issue 相关内容"""
    print(f"\n🔄 开始一键沉淀 Issue #{issue_id}...\n")
    
    results = []
    
    # 1. 更新 Issue 进度
    results.append(("进度更新", update_issue_progress(issue_id, summary, agent)))
    
    # 2. 同步到 Obsidian（知识类型）
    obsidian_content = f"# Issue #{issue_id} 完成总结\n\n"
    obsidian_content += f"**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    obsidian_content += f"## 完成说明\n\n{summary}\n\n"
    if learnings:
        obsidian_content += f"## 经验教训\n\n{learnings}\n"
    
    results.append(("Obsidian 同步", sync_to_obsidian(
        content=obsidian_content,
        content_type="knowledge",
        agent=agent or "system",
        title=f"Issue-{issue_id}-完成总结"
    )))
    
    # 3. 更新 MEMORY.md（如果有经验教训）
    if learnings and agent:
        memory_content = f"**Issue #{issue_id}**: {summary}\n\n**经验教训**:\n{learnings}"
        results.append(("MEMORY.md 更新", update_memory(agent, memory_content)))
    
    # 4. 添加交付物（如果有）
    if file_path:
        results.append(("交付物添加", add_deliverable(issue_id, file_path, summary)))
        results.append(("桌面工作空间", copy_to_desktop_workspace(issue_id, file_path)))
    
    # 输出结果
    print("\n" + "=" * 50)
    print("📊 沉淀结果")
    print("=" * 50)
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")
    
    success_count = sum(1 for _, s in results if s)
    print(f"\n总计: {success_count}/{len(results)} 成功")
    
    return all(s for _, s in results)


def quick_sync_daily(agent: str, summary: str):
    """一键同步每日总结"""
    print(f"\n🔄 开始每日沉淀 ({agent})...\n")
    
    results = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 同步到 Obsidian（日记类型）
    diary_content = f"# {today} 工作日志\n\n"
    diary_content += f"**Agent**: {agent}\n\n"
    diary_content += f"## 今日总结\n\n{summary}\n"
    
    results.append(("Obsidian 日记", sync_to_obsidian(
        content=diary_content,
        content_type="diary",
        agent=agent,
        title=f"{today} 工作日志"
    )))
    
    # 2. 更新本地日志
    try:
        if agent == "leader":
            workspace = BASE_DIR / "workspace"
        else:
            workspace = BASE_DIR / f"workspace-{agent}"
        
        memory_dir = workspace / "memory"
        memory_dir.mkdir(exist_ok=True)
        
        log_file = memory_dir / f"{today}.md"
        
        if log_file.exists():
            existing = log_file.read_text(encoding="utf-8")
            new_content = existing + f"\n\n## 每日总结\n\n{summary}\n"
        else:
            new_content = f"# {today} 工作日志\n\n## 每日总结\n\n{summary}\n"
        
        log_file.write_text(new_content, encoding="utf-8")
        print(f"✅ 本地日志已更新: {log_file}")
        results.append(("本地日志", True))
    except Exception as e:
        print(f"⚠️ 更新本地日志失败: {e}")
        results.append(("本地日志", False))
    
    # 输出结果
    print("\n" + "=" * 50)
    print("📊 每日沉淀结果")
    print("=" * 50)
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")
    
    return all(s for _, s in results)


def main():
    parser = argparse.ArgumentParser(description="一键沉淀脚本")
    parser.add_argument("--issue", "-i", type=int, help="Issue ID")
    parser.add_argument("--summary", "-s", required=True, help="完成说明/总结")
    parser.add_argument("--learnings", "-l", help="经验教训")
    parser.add_argument("--file", "-f", help="交付物文件路径")
    parser.add_argument("--agent", "-a", help="Agent 名称")
    parser.add_argument("--daily", "-d", action="store_true", help="每日总结模式")
    
    args = parser.parse_args()
    
    if args.daily:
        if not args.agent:
            print("❌ 每日总结模式需要指定 --agent")
            sys.exit(1)
        success = quick_sync_daily(args.agent, args.summary)
    elif args.issue:
        success = quick_sync_issue(
            issue_id=args.issue,
            summary=args.summary,
            learnings=args.learnings,
            file_path=args.file,
            agent=args.agent
        )
    else:
        print("❌ 请指定 --issue 或 --daily")
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
