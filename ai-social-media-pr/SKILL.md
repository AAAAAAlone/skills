---
name: ai-social-media-pr
description: Open social media profile URL, check login state, capture screenshot, and analyze whether the creator matches a configured type and tone (e.g. maternal and baby blogger, refined mom). Supports configurable blogger types and tones. Use when judging creator profiles from Douyin or similar platforms, screening for 母婴博主 (maternal/baby blogger), 调性 (tone), or when the user mentions AI Social Media PR, creator screening, or profile screenshot analysis.
---

# AI Social Media PR（AI 社媒 PR）

对社媒达人主页进行截图分析，判断是否符合配置的**博主类型**与**调性**（默认：母婴博主、精致妈妈）。核心流程：打开 URL → 检查登录 → 截图 → 文本/OCR/封面分析 → 输出类型分与调性分（1–10）。

## 核心能力

1. **打开 URL**：在浏览器中打开达人主页 URL。
2. **登录检查**：判断是否已登录；未登录则提示用户完成登录后再继续。
3. **截图**：登录完成后对当前页面截图（含顶部栏与左侧栏，由分析端按配置裁剪）。
4. **分析**：对截图做切格（4×6=24 个笔记格）、封面视觉分析、文案/标题匹配，结合**达人名称、简介、每个笔记标题**（由外部脚本稳定提供，本 skill 视为“已有”输入）判断是否母婴博主、调性是否较好。
5. **可配置**：博主类型与调性支持配置，后续可扩展为其他类型/调性；当前默认「母婴」。

## 样本文件夹（由你提供截图）

- **samples/nice/**：特别好的、完全符合标准的截图（约 10 张）。
- **samples/positive/**：还不错、符合要求的截图（约 10 张）。
- **samples/negative/**：不符合的截图（约 10 张）。

均为 4×6=24 个笔记的整页截图，含顶部登录栏与左侧导航栏。

截图格式统一为：整页包含顶部栏与左侧栏，内容区为 4 行×6 列=24 个笔记。分析时通过配置的裁剪比例排除顶栏与左栏，只对 24 格内容做切分与判断。

## 达人名称、简介、笔记标题

三者视为**已由外部脚本或流程提供**，本 skill 不依赖 AI 识别这些字段。调用分析接口时传入：

- `creator_name`：达人名称
- `creator_desc`：达人简介
- `note_titles`：24 个笔记的标题列表（与 24 格一一对应）

若未传入则使用切格后文案区 OCR 作为补充，但推荐由稳定脚本提供。

## 项目结构

```
ai-social-media-pr/
├── SKILL.md
├── README.md
├── reference.md
├── samples/
│   ├── nice/         # 完全符合标准（约 10 张）
│   ├── positive/     # 符合要求（约 10 张）
│   └── negative/     # 不符合（约 10 张）
├── data/             # 准则与参考向量（按 profile 可区分）
├── profiles/         # 可配置的博主类型/调性（当前默认母婴）
├── scripts/
│   ├── open_and_screenshot.py   # 打开 URL、检查登录、截图
│   └── judge.py                  # 对截图做分析并输出分数
├── config.py
├── grid.py
├── ...（分析相关模块）
└── requirements.txt
```

## 使用流程

### 1. 安装依赖

```bash
cd ai-social-media-pr
pip install -r requirements.txt
# 需安装 Tesseract 及中文语言包（OCR）
# Vision 需配置 OPENAI_API_KEY 或 GEMINI_API_KEY 等
```

### 2. 放入样本截图

将约 10 张正面案例放入 `samples/positive/`，约 10 张负面案例放入 `samples/negative/`。

### 3. 打开 URL 并截图

```bash
python scripts/open_and_screenshot.py "https://www.douyin.com/user/xxx" --output ./screenshot.png
```

脚本会打开 URL，检查是否已登录（未登录则提示用户登录后按回车），然后对页面截图保存到 `--output`。

### 4. 分析截图（假定已有达人名、简介、标题）

```bash
python scripts/judge.py ./screenshot.png --output ./judge_out \
  --creator-name "达人名" --creator-desc "简介" \
  --note-titles '["标题1","标题2",...]'
```

或由外部先提供 `creator_name`、`creator_desc`、`note_titles` 的 JSON/文件，再在脚本中传入。输出为类型分、调性分（1–10）及是否符合/非常符合。

### 5. 从样本生成准则与参考向量（可选）

使用 `samples/positive/` 与 `samples/negative/` 中的截图归纳准则并生成封面向量，用于后续判断时的相似度加分与准则注入。详见 `reference.md`。

## 配置

- **网格与裁剪**：`config.py` 中为 4×6=24 格；`CROP_TOP`/`CROP_LEFT` 等用于排除顶部登录栏与左侧导航栏。
- **博主类型与调性**：`profiles/` 下每个子目录为一套配置。默认 **douyin_mom_finder**（母婴奶粉场景）：含 `scoring.json` 规则打分（1–10，完全符合≥8.5）、两项细化（仅 0–3 岁婴幼儿计分、封面杂乱/广告感降调性）。可新增其他 profile 以支持不同达人要求。

## 何时使用本 Skill

- 用户需要判断某社媒达人是否为母婴博主、调性是否合适时。
- 用户提到「AI 社媒 PR」「达人筛选」「主页截图分析」「母婴博主」「调性」时。
- 用户需要打开达人主页 URL、确认登录后截图并做自动化分析时。
