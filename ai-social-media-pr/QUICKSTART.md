# 快速开始

## 1. 安装

```bash
git clone <your-repo-url> ai-social-media-pr
cd ai-social-media-pr
pip install -r requirements.txt
playwright install chromium
```

配置环境变量（Vision API）：
```bash
export OPENAI_API_KEY=sk-...  # 或 GEMINI_API_KEY / ANTHROPIC_API_KEY
```

## 2. 准备样本（可选，用于生成参考向量）

将截图放入：
- `samples/nice/`：完全符合标准（约 10 张）
- `samples/positive/`：符合要求（约 10 张）
- `samples/negative/`：不符合（约 10 张）

## 3. 生成参考向量（可选，提升准确度）

从 `samples/nice/` 自动提取正例特征并生成向量库：

```bash
python scripts/build_ref_from_samples.py
```

会生成 `profiles/douyin_mom_finder/ref_embeddings.json`，后续 judge 会自动使用。

## 4. 使用

### 方式一：打开 URL 并分析

```bash
# 1) 打开 URL，检查登录，截图
python scripts/open_and_screenshot.py "https://www.douyin.com/user/xxx" -o screenshot.png

# 2) 分析（传入达人名、简介）
python scripts/judge.py screenshot.png -o judge_out \
  --creator-name "达人名" --creator-desc "简介"
```

### 方式二：直接分析已有截图

```bash
python scripts/judge.py /path/to/screenshot.png -o judge_out \
  --creator-name "xxx" --creator-desc "xxx"
```

## 5. 输出

查看 `judge_out/result.json`：

```json
{
  "score_total": 8.2,
  "qualifies": true,      // >6 合格
  "very_recommended": false,  // >9 非常推荐
  "rule_breakdown": {...},
  "refinements": {
    "infant_cells_count": 6,
    "clutter_cells_count": 2
  }
}
```

控制台会打印：`总分: 8.2  合格>6: True  非常推荐>9: False`

## 特性

- **向量化特征提炼**：从 samples/nice 自动生成参考向量，judge 时做相似度比对，提升准确度
- **规则打分**：基于 scoring.json 的明确规则（置顶、婴幼儿数量、实物、场景等）
- **两项细化**：仅 0-3 岁婴幼儿计分；封面杂乱/广告感降调性
- **可配置**：通过 profile 支持不同达人类型与调性
