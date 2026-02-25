# 八步自我迭代流程与三层记忆融合方案

**Issue #10 [P1]** - Dev 设计文档  
**日期**: 2026-02-25  
**状态**: 设计中

---

## 1. 核心架构

### 1.1 系统概览

```
┌─────────────────────────────────────────────────────────────┐
│                    八步自我迭代流程                          │
│  观察 → 分析 → 设计 → 实施 → 验证 → 记录 → 提炼 → 提交      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    三层记忆系统                              │
│                                                              │
│  第一层：每日日志 (memory/YYYY-MM-DD.md)                    │
│  ├─ 迭代过程实时记录                                        │
│  └─ 临时数据、执行日志                                      │
│                                                              │
│  第二层：长期记忆 (MEMORY.md)                               │
│  ├─ 迭代结果摘要 (带优先级 P0-P3)                          │
│  ├─ 提炼的知识和规律                                        │
│  └─ TTL 管理 (P0永久, P1 90天, P2 30天, P3 7天)           │
│                                                              │
│  第三层：索引系统 (memory/index.json)                       │
│  ├─ 关键词索引 (快速检索)                                   │
│  ├─ 标签索引 (#tag)                                        │
│  ├─ 优先级索引 ([P0-P3])                                   │
│  └─ 自动触发检测 (重复问题识别)                            │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 数据流

```
问题发生
    ↓
搜索索引 (第三层) → 发现重复 ≥ 2 次？
    ↓ 是
触发八步流程
    ↓
步骤 1-5: 执行阶段
    ├─ 实时写入每日日志 (第一层)
    └─ 创建 memory/iterations/YYYYMMDD-HHmm.md
    ↓
步骤 6: 记录阶段
    ├─ 完整迭代记录
    └─ 写入 MEMORY.md (第二层, 带优先级)
    ↓
步骤 7: 提炼阶段
    ├─ 提炼通用规律
    ├─ 写入 MEMORY.md 或强制规则
    └─ 触发索引重建 (第三层)
    ↓
步骤 8: 提交阶段
    ├─ 更新系统文件
    ├─ 通知相关人员
    └─ 索引自动更新完成
```

---

## 2. 关键组件设计

### 2.1 迭代触发器 (IterationTrigger)

**职责**: 检测重复问题，决定是否启动迭代

**核心逻辑**:
```python
class IterationTrigger:
    def check_repetition(self, problem_signature: str) -> bool:
        """检查问题是否重复出现"""
        # 1. 搜索索引 (第三层)
        results = memory_indexer.search(problem_signature)
        
        # 2. 统计出现次数
        count = len(results)
        
        # 3. 判断是否触发
        if count >= 2:
            return True, count
        return False, count
    
    def suggest_iteration(self, problem: str, count: int):
        """主动提示用户启动迭代"""
        message = f"⚠️ 这是第 {count} 次遇到「{problem}」，建议启动迭代流程来解决。是否开始？"
        return message
```

**触发条件**:
1. 同样问题出现 ≥ 2 次（通过索引检测）
2. 用户明确要求改进
3. 发现明显的效率问题

### 2.2 迭代执行器 (IterationExecutor)

**职责**: 执行八步流程，管理数据写入

**核心逻辑**:
```python
class IterationExecutor:
    def __init__(self):
        self.current_iteration = None
        self.daily_log = Path(f"memory/{datetime.now().strftime('%Y-%m-%d')}.md")
        self.iteration_dir = Path("memory/iterations")
    
    def start_iteration(self, problem: str):
        """开始迭代流程"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        
        self.current_iteration = {
            "id": timestamp,
            "problem": problem,
            "steps": {},
            "start_time": datetime.now().isoformat()
        }
        
        # 在每日日志中记录开始
        self._log_to_daily(f"## 🔄 迭代开始 - {timestamp}\n问题: {problem}\n")
    
    def execute_step(self, step_num: int, step_name: str, output: str):
        """执行单个步骤"""
        self.current_iteration["steps"][step_num] = {
            "name": step_name,
            "output": output,
            "timestamp": datetime.now().isoformat()
        }
        
        # 实时写入每日日志 (第一层)
        self._log_to_daily(f"### 步骤 {step_num}: {step_name}\n{output}\n\n")
    
    def finalize_iteration(self):
        """完成迭代，写入第二层和第三层"""
        # 1. 创建完整迭代记录
        iteration_file = self.iteration_dir / f"{self.current_iteration['id']}.md"
        self._write_iteration_record(iteration_file)
        
        # 2. 写入 MEMORY.md (第二层)
        self._write_to_memory_md()
        
        # 3. 触发索引重建 (第三层)
        self._rebuild_index()
```

### 2.3 记忆写入器 (MemoryWriter)

**职责**: 将迭代结果写入不同记忆层级

**第一层写入** (每日日志):
```markdown
## 🔄 迭代记录 - 20260225-1145

### 问题
每次创建文件都要问"保存到哪里"

### 步骤 1: 观察
- 频率: 每天 5-10 次
- 影响: 决策疲劳、效率低

### 步骤 2: 分析
- 原因: 没有存储路由规则
- 根本原因: 系统不知道不同类型文件应该放哪里

[... 其他步骤 ...]
```

**第二层写入** (MEMORY.md):
```markdown
## [P1] 智能存储路由
<!-- TTL: 90d -->

**问题**: 每次创建文件都要手动指定位置，造成决策疲劳

**解决方案**: 实施智能存储路由规则，根据文件类型自动决定存储位置

**效果**: 
- 减少决策次数 80%
- 文件位置更规范
- 提升工作效率

**实施时间**: 2026-02-25  
**迭代记录**: memory/iterations/20260225-1145.md

**提炼的规律**:
- 重复性决策应该自动化
- 文件类型可以自动识别
- 规则优于询问
```

**第三层更新** (索引):
```json
{
  "keywords": {
    "存储路由": ["MEMORY.md#L123", "memory/2026-02-25.md#L45"],
    "决策疲劳": ["MEMORY.md#L123"],
    "自动化": ["MEMORY.md#L123", "MEMORY.md#L89"]
  },
  "tags": {
    "optimization": ["MEMORY.md#L123"],
    "automation": ["MEMORY.md#L123"]
  },
  "priorities": {
    "P1": [
      {
        "title": "智能存储路由",
        "location": "MEMORY.md#L123"
      }
    ]
  }
}
```

---

## 3. 自动触发机制

### 3.1 问题签名生成

**目的**: 识别相似问题

**方法**:
```python
def generate_problem_signature(problem_text: str) -> str:
    """生成问题签名用于检测重复"""
    # 1. 提取关键词
    keywords = extract_keywords(problem_text)
    
    # 2. 标准化
    normalized = normalize_keywords(keywords)
    
    # 3. 生成签名
    signature = "-".join(sorted(normalized))
    
    return signature

# 示例:
# "每次创建文件都要问保存位置" → "创建-文件-保存-位置"
# "创建文件时需要手动指定路径" → "创建-文件-路径-指定"
# 两者签名相似度高 → 识别为同一问题
```

### 3.2 重复检测流程

```python
def detect_repetition(problem: str) -> tuple[bool, int, list]:
    """检测问题是否重复"""
    # 1. 生成问题签名
    signature = generate_problem_signature(problem)
    
    # 2. 搜索索引
    results = memory_indexer.search(signature)
    
    # 3. 过滤相关结果
    relevant = filter_relevant_results(results, signature)
    
    # 4. 统计次数
    count = len(relevant)
    
    # 5. 判断是否触发
    should_trigger = count >= 2
    
    return should_trigger, count, relevant
```

### 3.3 主动提示

**时机**: 检测到重复问题时

**提示语**:
```
⚠️ 重复问题检测

我注意到「{problem}」这个问题已经是第 {count} 次出现了。

之前的记录:
1. {date1} - {location1}
2. {date2} - {location2}

建议启动八步自我迭代流程来彻底解决这个问题。

是否开始迭代？[Y/n]
```

---

## 4. 实施方案

### 4.1 第一阶段：核心框架（2 天）

**任务**:
1. 创建 `iteration_engine.py` - 迭代引擎
2. 实现 IterationTrigger - 触发器
3. 实现 IterationExecutor - 执行器
4. 实现 MemoryWriter - 记忆写入器

**交付物**:
- 可以手动触发迭代流程
- 迭代记录正确写入三层记忆
- 基本的重复检测功能

### 4.2 第二阶段：自动触发（1 天）

**任务**:
1. 实现问题签名生成
2. 实现重复检测逻辑
3. 集成到系统提示中
4. 添加主动提示功能

**交付物**:
- AI 可以主动检测重复问题
- 自动提示用户启动迭代
- 触发条件可配置

### 4.3 第三阶段：知识沉淀（1 天）

**任务**:
1. 实现知识提炼逻辑
2. 自动更新强制规则
3. 索引自动重建
4. 知识可检索验证

**交付物**:
- 提炼的知识自动索引
- 强制规则自动更新
- 知识可以被检索和复用

### 4.4 第四阶段：测试优化（1 天）

**任务**:
1. 端到端测试
2. 性能优化
3. 文档完善
4. 使用培训

**交付物**:
- 完整的使用文档
- 测试报告
- 性能基准

---

## 5. 技术细节

### 5.1 文件结构

```
~/.openclaw/workspace-dev/
├── scripts/
│   ├── iteration_engine.py          # 迭代引擎（新增）
│   ├── memory_indexer.py            # 索引器（已有）
│   ├── memory_ttl.py                # TTL 管理（已有）
│   └── unified_memory_maintenance.py # 统一维护（已有）
├── memory/
│   ├── YYYY-MM-DD.md                # 每日日志（第一层）
│   ├── index.json                   # 索引（第三层）
│   ├── iterations/                  # 迭代记录目录（新增）
│   │   ├── template.md              # 迭代模板
│   │   └── YYYYMMDD-HHmm.md        # 具体迭代记录
│   └── archive/                     # 归档目录
└── MEMORY.md                        # 长期记忆（第二层）
```

### 5.2 数据格式

**迭代记录格式** (`memory/iterations/YYYYMMDD-HHmm.md`):
```markdown
# 迭代记录 - YYYYMMDD-HHmm

## 元数据
- ID: YYYYMMDD-HHmm
- 问题: {problem}
- 开始时间: {start_time}
- 完成时间: {end_time}
- 优先级: P1
- 标签: #optimization #automation

## 步骤 1: 观察
{observation}

## 步骤 2: 分析
{analysis}

## 步骤 3: 设计
{design}

## 步骤 4: 实施
{implementation}

## 步骤 5: 验证
{verification}

## 步骤 6: 记录
{record}

## 步骤 7: 提炼
{distillation}

## 步骤 8: 提交
{submission}

## 总结
- 问题解决: ✅
- 效果评估: {effect}
- 知识沉淀: {knowledge}
```

---

## 6. 使用示例

### 6.1 手动触发迭代

```python
# 用户发现问题
user: "每次创建文件都要问保存位置，能改进吗？"

# AI 启动迭代
ai: "收到！启动八步自我迭代流程..."

# 执行八步
ai.execute_iteration(
    problem="每次创建文件都要问保存位置",
    steps=[
        ("观察", "频率: 每天 5-10 次..."),
        ("分析", "原因: 没有存储路由规则..."),
        # ... 其他步骤
    ]
)

# 完成后通知
ai: "✅ 迭代完成！已实施智能存储路由规则。"
```

### 6.2 自动触发迭代

```python
# 问题第一次发生
user: "这个文件应该保存到哪里？"
ai: "建议保存到 workspace-dev/docs/"
# 记录到索引

# 问题第二次发生
user: "这个文件应该保存到哪里？"
ai: "⚠️ 这是第 2 次遇到这个问题，建议启动迭代流程来解决。是否开始？"
user: "是"
ai: "收到！启动八步自我迭代流程..."
```

---

## 7. 预期效果

### 7.1 量化指标

| 指标 | 当前 | 目标 | 提升 |
|------|------|------|------|
| 重复问题解决率 | 0% | 80% | +80% |
| 系统自我改进次数 | 0次/月 | 10次/月 | +10 |
| 知识沉淀速度 | 手动 | 自动 | 10x |
| 问题检测准确率 | N/A | 90% | - |

### 7.2 质量指标

- ✅ AI 可以主动发现重复问题
- ✅ 迭代流程标准化、可追溯
- ✅ 知识自动沉淀、可检索
- ✅ 系统持续自我优化

---

**状态**: 核心架构设计完成，等待 Leader 审核
**下一步**: 开始实施第一阶段（核心框架）
