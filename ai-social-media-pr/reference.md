# AI Social Media PR - 使用说明

## 仓库名与技能名

- **中文**：AI 社媒 PR（AI Social Media PR）
- **英文**：AI Social Media PR
- **Skill 名**：`ai-social-media-pr`

## 样本截图

- **samples/nice/**：完全符合标准（约 10 张）
- **samples/positive/**：符合要求（约 10 张）
- **samples/negative/**：不符合（约 10 张）

分析时通过 `config.py` 的 `CROP_TOP`、`CROP_LEFT` 等比例排除顶栏与左栏，只对 24 格内容切分与判断。若实际截图比例与默认不一致，可调整：

- `CROP_TOP`：排除顶部登录栏（默认 0.10）
- `CROP_LEFT`：排除左侧导航栏（默认 0.08）

## 达人名称、简介、笔记标题

三者视为**已由外部脚本或流程提供**，本 skill 不依赖 AI 识别。调用 `scripts/judge.py` 时传入：

- `--creator-name`：达人名称
- `--creator-desc`：达人简介
- `--note-titles '["标题1","标题2",...]'`：24 个笔记标题的 JSON 数组（不足 24 个会补空串，多出截断）

未传入时使用切格后文案区 OCR 作为补充。

## 可配置博主类型与调性

- 默认 **profiles/douyin_mom_finder/**：含 `scoring.json` 规则打分（1–10，完全符合≥8.5）、`criteria_type.json` / `criteria_tone.json`。规则包括：置顶前三位真实带娃、24 格中>5 格婴幼儿元素、奶粉/纸尿裤等实物、真实居家场景、无 AI 军装、名字/简介关键词。两项细化：仅 0–3 岁小宝宝计为婴幼儿；封面杂乱/广告感降调性。
- 使用 **profiles/maternal_baby/** 时无 `scoring.json`，按准则做类型/调性双维度打分。
- 后续可新增 profile（如 `profiles/food_blogger/`）：复制目录结构，放入 `scoring.json`（可选）与 `criteria_type.json`、`criteria_tone.json`，用 `--profile <name>` 指定。

## 流程

1. **打开 URL 并截图**  
   `python scripts/open_and_screenshot.py "https://www.douyin.com/user/xxx" -o screenshot.png`  
   会打开浏览器，若检测到「登录」按钮则提示用户登录后按回车，再截图。

2. **分析截图**（假定已有达人名、简介、标题）  
   `python scripts/judge.py screenshot.png -o judge_out --creator-name "xxx" --creator-desc "xxx" --note-titles '["t1",...]'`  
   输出类型分、调性分（1–10）及是否符合/非常符合。

3. **从样本生成参考向量（可选）**  
   对 `samples/positive/` 下某张截图的切分结果运行 `build_ref_store_from_sliced.py`（或对已切分目录指定正例格子索引），生成 `ref_embeddings.json`，再在 judge 时通过 `--ref-store` 传入，用于封面向量相似度加分。

## 安装

```bash
pip install -r requirements.txt
playwright install chromium
# OCR 需安装 Tesseract 及 chi_sim 语言包
# Vision 需配置 OPENAI_API_KEY 或 GEMINI_API_KEY 等
```

运行脚本时需在项目根目录或确保 `scripts/` 能正确解析到项目根（脚本已做 `sys.path.insert(PROJECT_ROOT)`）。
