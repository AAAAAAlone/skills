# GitHub 推送检查清单

## ✅ 已完成

1. **打分机制**：1-10 分，>6 合格，>9 非常推荐 ✓
2. **向量化特征提炼**：
   - `scripts/build_ref_from_samples.py`：从 samples/nice 自动提取正例格子并生成参考向量
   - `judge.py` 默认使用 `profiles/<profile>/ref_embeddings.json`（如果存在）
   - 使用 sentence-transformers (CLIP) 做图像向量化，不只是提示词优化
3. **通用性与部署**：
   - Profile 驱动，支持不同达人类型
   - 文档完整（README、QUICKSTART、DEPLOY、SKILL）
   - .gitignore 已配置

## 推送前检查

### 1. 确认敏感信息已忽略

```bash
# 检查 .gitignore
cat .gitignore

# 确认以下文件/目录不会被提交：
# - *.png, *.jpg (除 samples/)
# - ref_embeddings.json
# - .env
# - judge_out/, sliced/, temp_sliced/
```

### 2. 确认样本目录结构

```bash
# samples 目录应存在
ls -la samples/nice/
ls -la samples/positive/
ls -la samples/negative/
```

### 3. 初始化 Git（如未初始化）

```bash
cd ai-social-media-pr
git init
git add .
git commit -m "Initial commit: AI Social Media PR skill"
```

### 4. 创建 GitHub 仓库并推送

```bash
# 在 GitHub 创建新仓库（名称：ai-social-media-pr）
# 然后：
git remote add origin https://github.com/<your-username>/ai-social-media-pr.git
git branch -M main
git push -u origin main
```

## 安装验证（推送后）

在另一台机器或龙虾上验证：

```bash
git clone https://github.com/<your-username>/ai-social-media-pr.git
cd ai-social-media-pr
pip install -r requirements.txt
playwright install chromium
export OPENAI_API_KEY=sk-...

# 测试向量生成（如果有 samples/nice）
python scripts/build_ref_from_samples.py

# 测试 judge（使用示例截图）
python scripts/judge.py <screenshot.png> -o test_out --creator-name "测试" --creator-desc "测试"
```

## 注意事项

- **API 密钥**：不要提交到仓库，通过环境变量传入
- **参考向量**：`ref_embeddings.json` 较大，已在 .gitignore 中，首次使用时需运行 `build_ref_from_samples.py` 生成
- **样本截图**：samples/ 目录下的截图可选择性提交（用于示例），或只保留 .gitkeep
