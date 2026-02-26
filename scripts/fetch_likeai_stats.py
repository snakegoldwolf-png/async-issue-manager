#!/usr/bin/env python3
"""
Like·AI 统计数据抓取脚本
定时抓取 API 使用统计，缓存到本地 JSON 文件
API Key 只在服务端使用，不暴露到前端
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.error

# 数据缓存路径
CACHE_DIR = Path.home() / ".openclaw/shared/async-issue-manager/.cache"
CACHE_FILE = CACHE_DIR / "likeai_stats.json"

# API Key 从环境变量读取（安全）
API_KEY_ENV = "LIKEAI_API_KEY"

# Like·AI API 端点
LIKEAI_API_URL = "https://like-ai.cc/api/user/self"


def get_api_key():
    """从环境变量或安全配置文件获取 API Key"""
    # 优先从环境变量读取
    api_key = os.environ.get(API_KEY_ENV)
    if api_key:
        return api_key
    
    # 从安全配置文件读取（仅限服务端）
    secret_file = Path.home() / ".openclaw/.secrets/likeai_key"
    if secret_file.exists():
        return secret_file.read_text().strip()
    
    return None


def fetch_likeai_stats(api_key: str) -> dict:
    """从 Like·AI API 获取统计数据"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "OpenClaw-Dashboard/1.0"
    }
    
    try:
        req = urllib.request.Request(LIKEAI_API_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error fetching stats: {e}", file=sys.stderr)
        return None


def save_cache(data: dict):
    """保存统计数据到缓存文件"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    cache_data = {
        "fetched_at": datetime.now().isoformat(),
        "source": "like-ai.cc",
        "data": data
    }
    
    CACHE_FILE.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2))
    print(f"✅ 统计数据已缓存到: {CACHE_FILE}")


def load_cache() -> dict:
    """加载缓存的统计数据"""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except:
            return None
    return None


def main():
    """主函数：抓取并缓存统计数据"""
    api_key = get_api_key()
    
    if not api_key:
        print(f"❌ 未找到 API Key。请设置环境变量 {API_KEY_ENV} 或创建 ~/.openclaw/.secrets/likeai_key 文件", file=sys.stderr)
        sys.exit(1)
    
    print("🔄 正在从 Like·AI 获取统计数据...")
    stats = fetch_likeai_stats(api_key)
    
    if stats:
        save_cache(stats)
        
        # 打印摘要（不包含敏感信息）
        if isinstance(stats, dict):
            print(f"📊 统计摘要:")
            if 'data' in stats:
                d = stats['data']
                print(f"   - 请求数: {d.get('request_count', 'N/A')}")
                print(f"   - Token 数: {d.get('used_quota', 'N/A')}")
    else:
        print("❌ 获取统计数据失败", file=sys.stderr)
        # 尝试使用缓存
        cached = load_cache()
        if cached:
            print(f"📦 使用缓存数据 (更新于: {cached.get('fetched_at', 'unknown')})")
        sys.exit(1)


if __name__ == "__main__":
    main()
