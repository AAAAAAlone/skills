# 部署说明（GitHub + 龙虾）

本仓库设计为可克隆到任意环境（含龙虾）运行，通过 profile 支持不同达人类型与调性，无需改代码即可切换或扩展。

## 通用性

- **Profile 驱动**：所有「博主类型、调性、打分规则」均在 `profiles/<name>/` 下配置。
  - 若目录内存在 **scoring.json**：使用规则打分（如 douyin_mom_finder），输出 `score_total`（1-10）、`qualifies`（>6 合格）、`very_recommended`（>9 非常推荐）。
  - 若无 scoring.json：使用 **criteria_type.json** + **criteria_tone.json** 做类型/调性双维度打分。
  - **ref_embeddings.json**（可选）：从 `samples/nice/` 自动生成的参考向量库，用于相似度加分，提升准确度。
- **新增达人要求**：复制一份 profile（如 `profiles/douyin_mom_finder`）并改名，按需修改：
  - `scoring.json`：`rules`、`perfect_match_threshold`、`grid_scope` 等；
  - `criteria_type.json` / `criteria_tone.json`：关键词与正负向描述。
- **样本数据**：`samples/nice`、`samples/positive`、`samples/negative` 用于：
  - 人工标注参考
  - 运行 `build_ref_from_samples.py` 自动生成参考向量（从 nice 目录提取正例格子特征）
  - 运行 judge 时不依赖这些图片，只依赖 profile 配置、Vision API 与可选的参考向量库

## 环境要求

- Python 3.9+
- 依赖：`pip install -r requirements.txt`；Playwright：`playwright install chromium`
- OCR：Tesseract + 中文语言包（如 chi_sim）
- Vision：`OPENAI_API_KEY` 或 `GEMINI_API_KEY` 或 `ANTHROPIC_API_KEY` 之一

## 克隆与安装（含龙虾）

```bash
git clone <your-repo-url> ai-social-media-pr
cd ai-social-media-pr
pip install -r requirements.txt
playwright install chromium
```

龙虾上若为无头环境，截图步骤可改为由外部传入截图文件，仅运行 `scripts/judge.py` 做分析；或使用 `scripts/open_and_screenshot.py --headless`（不检查登录，直接截图）。

## 运行方式

- **打开 URL 并截图**：  
  `python scripts/open_and_screenshot.py "https://www.douyin.com/user/xxx" -o screenshot.png`

- **分析截图**（默认 profile：douyin_mom_finder）：  
  `python scripts/judge.py screenshot.png -o judge_out --creator-name "xxx" --creator-desc "xxx"`

- **使用其他 profile**：  
  `python scripts/judge.py screenshot.png -o judge_out -p maternal_baby`

- **从样本生成参考向量**（可选，提升准确度）：  
  `python scripts/build_ref_from_samples.py`  
  会处理 `samples/nice/` 下所有截图，提取正例格子（0-3岁婴幼儿、真实居家、非杂乱），生成 `profiles/douyin_mom_finder/ref_embeddings.json`。后续 judge 时会自动使用该向量库做相似度加分。

- **输出**：`judge_out/result.json` 及控制台打印。douyin_mom_finder 模式下含 `score_total`（1-10）、`qualifies`（>6 合格）、`very_recommended`（>9 非常推荐）、`rule_breakdown`、`refinements`（婴幼儿格数、杂乱格数等）。

## 配置与密钥

- 网格与裁剪：`config.py` 中 `CROP_TOP`、`CROP_LEFT`、`GRID_ROWS`、`GRID_COLS`。
- API 密钥：通过环境变量传入，不要提交到仓库。

## 提交到 GitHub

- 确保 `.gitignore` 已忽略 `*.png`、`ref_embeddings.json`、`.env` 等。
- 样本目录 `samples/nice`、`samples/positive`、`samples/negative` 可保留 `.gitkeep` 或放入少量示例截图（按需）。
- README、SKILL.md、DEPLOY.md 已包含使用与部署说明，可直接推送。
