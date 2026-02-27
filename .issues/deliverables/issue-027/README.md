# Nano Banana 2.0 图像生成 Skill

使用 Google Gemini 3.1 Flash Image 模型（Nano Banana 2.0）生成高质量图像。

## 位置

```
~/.openclaw/workspace/skills/nano-banana-2/
├── generate.py    # 主脚本
├── README.md      # 本文档
└── SKILL.md       # Skill 元数据
```

## 快速开始

```bash
cd ~/.openclaw/workspace/skills/nano-banana-2

# 生成一张图
python3 generate.py --prompt "一只可爱的橘猫在阳光下打盹"

# 指定比例和分辨率
python3 generate.py --prompt "sunset over mountains" --aspect 16:9 --size 2k

# JSON 输出
python3 generate.py --prompt "logo design" --json

# 指定输出路径
python3 generate.py --prompt "abstract art" --output ~/Desktop/art.png
```

## 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--prompt` | `-p` | 图像描述（必需）| - |
| `--output` | `-o` | 输出文件路径 | 自动生成 |
| `--aspect` | `-a` | 宽高比 | 1:1 |
| `--size` | `-s` | 分辨率 | 1k |
| `--json` | - | JSON 格式输出 | false |

### 宽高比选项 (--aspect)

| 值 | 说明 |
|-----|------|
| `1:1` | 正方形（默认）|
| `16:9` | 横向宽屏 |
| `9:16` | 竖向（手机屏幕）|
| `4:3` | 传统横向 |
| `3:4` | 传统竖向 |
| `3:2` | 照片横向 |
| `2:3` | 照片竖向 |
| `21:9` | 超宽横幅 |
| `4:5` | Instagram 竖向 |
| `5:4` | Instagram 横向 |
| `auto` | 自动 |

### 分辨率选项 (--size)

| 值 | 像素 |
|-----|------|
| `1k` / `1024` | 1024px |
| `2k` / `2048` | 2048px |
| `4k` / `4096` | 4096px |

## API 配置

### 默认配置（已内置）

脚本已内置吾爱API的 API Key，开箱即用。

### 自定义 API Key

方式一：环境变量
```bash
export WUAI_API_KEY='your-api-key'
```

方式二：配置文件
```bash
mkdir -p ~/.openclaw/credentials
echo 'your-api-key' > ~/.openclaw/credentials/wuai_api_key
```

### API 详情

| 配置项 | 值 |
|--------|-----|
| API Base | `https://wuaiapi.com/v1beta` |
| Model | `gemini-3.1-flash-image-preview` |
| 格式 | Google Gemini 原生格式 |
| 定价 | 0.055 元/次（充值多 0.05 元/次）|

## 输出目录

默认输出到：`~/.openclaw/media/generated/`

文件名格式：`nano_banana_YYYYMMDD_HHMMSS.png`

## Python API

```python
from generate import generate_image, save_image

# 生成图像
result = generate_image(
    prompt="一只可爱的猫咪",
    aspect_ratio="1:1",
    resolution="1024"
)

if result["status"] == "success":
    path = save_image(result["image_data"])
    print(f"图像已保存到: {path}")
```

## 示例

### 生成风景图
```bash
python3 generate.py -p "misty mountains at sunrise, dramatic lighting, 8k photography" -a 16:9 -s 2k
```

### 生成人物头像
```bash
python3 generate.py -p "digital avatar of a software developer, minimalist style, blue lighting" -a 1:1 -s 2k
```

### 生成小红书封面
```bash
python3 generate.py -p "aesthetic flat lay of coffee and notebook, warm tones, cozy vibe" -a 3:4 -s 2k
```

### 生成 Logo
```bash
python3 generate.py -p "minimalist tech company logo, geometric shapes, blue and white" -a 1:1 -s 1k
```

## 注意事项

1. **配额限制**：免费用户每天最多 100 张
2. **保存图片**：生成后及时保存，避免内存溢出
3. **网络要求**：需要能访问 wuaiapi.com

## 更新日志

### 2026-02-27
- ✅ 初始版本
- ✅ 支持 Nano Banana 2.0 (gemini-3.1-flash-image-preview)
- ✅ 支持多种宽高比和分辨率
- ✅ 集成吾爱API中转服务

---

**作者**: Dev  
**创建日期**: 2026-02-27
