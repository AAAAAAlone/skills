# AI Social Media PR（AI 社媒 PR）

对社媒达人主页进行截图分析，判断是否符合配置的**博主类型**与**调性**（默认：母婴博主、精致妈妈）。支持打开 URL、登录检查、截图与文本/OCR/封面分析，可配置多种博主类型与调性。

## 能力概览

- 打开达人主页 URL，检查是否已登录，未登录则提示用户登录后继续。
- 对页面截图（4×6=24 个笔记的整页，含顶栏与侧栏；分析时按配置裁剪）。
- 结合达人名称、简介、每个笔记标题（由外部脚本提供）与封面视觉、文案，输出总分（1–10），**>6 合格，>9 非常推荐**。
- **向量化特征提炼**：从 `samples/nice/` 自动生成参考向量库，judge 时做相似度比对，提升准确度（不只是提示词优化）。

## 样本截图

请将截图放入以下目录（整页含顶栏与侧栏，内容区 4×6=24 个笔记）：

- **samples/nice/**：完全符合标准（约 10 张）
- **samples/positive/**：符合要求（约 10 张）
- **samples/negative/**：不符合（约 10 张）

默认使用 **douyin_mom_finder** profile：规则打分 1–10，**>6 合格，>9 非常推荐**；仅 0–3 岁婴幼儿计为有效，封面杂乱/广告感会降调性。

## 快速开始

```bash
pip install -r requirements.txt
playwright install chromium
export OPENAI_API_KEY=sk-...  # 或 GEMINI_API_KEY

# 可选：从 samples/nice 生成参考向量（提升准确度）
python scripts/build_ref_from_samples.py

# 1) 打开 URL 并截图（会检查登录）
python scripts/open_and_screenshot.py "https://www.douyin.com/user/xxx" -o screenshot.png

# 2) 分析（传入达人名、简介）
python scripts/judge.py screenshot.png -o judge_out --creator-name "xxx" --creator-desc "xxx"
```

详细说明见 [QUICKSTART.md](QUICKSTART.md) 和 [DEPLOY.md](DEPLOY.md)。
