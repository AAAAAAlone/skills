---
name: bilibili-video-to-text
description: 从 B 站视频链接获取完整转录文本和摘要，输出为带 YAML 元数据的 Markdown 文件。优先提取字幕，无字幕时下载视频并语音识别。支持 Agent 后处理：添加标点、修正错别字、去除语气词、逻辑分段。使用场景：用户提供 bilibili.com 链接、要求转文字、要摘要、要后处理、要整理口语文本、要生成知识库笔记。
---

# B 站视频转文本

## 触发条件

- 用户提供 B 站视频链接并要求转文字、转文本、提取内容、生成摘要、制作知识库笔记
- 用户对 bilibili-video-to-text 的输出文件要求「后处理」「整理」「加标点」「修正错别字」「去除语气词」「分段」

## 环境检测与安装

执行前先运行环境检测：

```bash
cd <skill 目录> && python scripts/check_env.py
```

根据输出的 JSON 中 `install_commands` 安装缺失依赖：

| 依赖 | Mac | Windows |
|------|-----|---------|
| Python 3.10+ | `brew install python` | `winget install Python.Python.3.12` |
| ffmpeg | `brew install ffmpeg` | `choco install ffmpeg` |
| yt-dlp | `pip install yt-dlp` | `pip install yt-dlp` |
| Whisper（无字幕时） | `pip install openai-whisper` | 同上 |

首次使用建议运行：`pip install -r requirements.txt`

## 主流程

1. **提取链接**：从用户消息中识别 B 站视频 URL
2. **环境检查**：运行 `check_env.py`，若 `ready_for_subtitle` 为 false，按 `install_commands` 指导安装
3. **执行转写**：

```bash
python scripts/bvt.py "https://www.bilibili.com/video/BVxxxxx" --output-dir <输出目录>
```

若 B 站视频有 CC 字幕但需登录，可加 `--cookies-from-browser chrome` 或 `safari`。

**结构化输出（两种方式）**：

| 方式 | 说明 |
|------|------|
| **Cursor Agent**（推荐，无需 API） | 转写完成后，将输出文件交给 Agent，说：「帮我对原文做后处理：添加标点、修正错别字、去除语气词、按逻辑分段」 |
| **Gemini API** | 加 `--post-process`，需设置 `GEMINI_API_KEY`（在 https://aix.google.dev 获取） |

```bash
# 方式 1：仅转写，后处理交给 Agent
python scripts/bvt.py "https://www.bilibili.com/video/BVxxxxx" -o output --cookies-from-browser chrome
# 然后对 Agent 说：帮我对 output/xxx.md 的原文做后处理

# 方式 2：脚本内自动后处理（需 API Key）
export GEMINI_API_KEY="你的API密钥"
python scripts/bvt.py "https://www.bilibili.com/video/BVxxxxx" -o output --post-process
```

4. **生成摘要**：脚本会输出带 YAML frontmatter 的 MD 文件，其中 `summary` 初值为占位符。Agent 读取原文后，生成 2–4 句摘要，替换 `summary:` 下的内容
5. **可选 tags**：根据视频标题和内容，在 YAML 中补充 `tags` 数组
6. **删除原始视频**：转写完成后，若 output 目录或工作目录中存在下载的视频/音频文件（`.mp4`、`.webm`、`.mp3`、`.m4a`），删除以释放空间

## Agent 后处理（固化能力）

当用户要求对转写原文做后处理，或原文为无标点、口语化、有错别字的连续文本时，Agent **必须**执行以下步骤：

### 后处理步骤

1. **读取**：读取目标 `.md` 文件中 `# 完整原文` 下的正文
2. **转换**：将口语转写文本转为规范书面语，执行：
   - **添加标点**：逗号、句号、问号、顿号等
   - **修正错别字**：同音字错误（如：客楼的部→Clawdbot、彩爆→财报、草骨→炒股、镜箱→镜像、造人→找人）
   - **去除语气词**：啊、呢、嗯、好吧、完了、听我说、这个这个、那个那个、就是说 等
   - **逻辑分段**：按语义分段，每段 2–4 句，段与段之间空一行
3. **写回**：用转换后的文本替换原 `# 完整原文` 下的内容
4. **摘要**：若 `summary` 为占位符，根据转换后原文生成 2–4 句摘要并更新

### 输出要求

- 保持原意不变，只做格式和语言规范化
- 专业术语、品牌名、产品名按常见写法修正（如 Clawdbot、PRD、Figma、飞书、钉钉）
- 段落不宜过长，便于阅读

### 触发话术

用户说以下任一即可触发后处理：「帮我对原文做后处理」「整理一下这段文字」「加标点」「修正错别字」「去除语气词」「分段」

## 输出格式

```yaml
---
title: "视频标题"
source: "https://www.bilibili.com/video/BVxxxxx"
source_type: bilibili
duration: "12:34"
processed_at: "2025-02-12T16:00:00"
tags:
  - AI
  - 教程
summary: |
  本视频介绍了……（Agent 生成的 2–4 句摘要）
---

# 完整原文

[按自然段分行的转录文本]
```

## 双路径策略

- **路径 A（优先）**：yt-dlp 拉取字幕（--lang zh-CN），解析 srt/vtt/ass 为纯文本
- **路径 B（兜底）**：无字幕时下载视频 → ffmpeg 提取音频 → Whisper 转写（需安装 openai-whisper）

## 学生使用指南（零基础）

### 第一步：安装 Cursor

从 https://cursor.sh 下载并安装 Cursor（需要 Pro 会员）

### 第二步：克隆本 Skill

打开 Cursor 的终端（Terminal），执行以下命令：

```bash
git clone https://github.com/<your-username>/bilibili-video-to-text.git ~/.cursor/skills/bilibili-video-to-text
cd ~/.cursor/skills/bilibili-video-to-text
```

如果你的电脑还没有安装 Git，在 Cursor 中对 Agent 说：「帮我安装 Git」

### 第三步：运行安装脚本

**Mac/Linux 用户：**

```bash
./setup.sh
```

**Windows 用户：**

在 PowerShell 中（可能需要管理员权限）：

```powershell
.\setup.ps1
```

脚本会自动：
- 检测并安装缺失的依赖（Python、ffmpeg、yt-dlp）
- 安装 Python 库
- 运行环境检测
- 可选择将 skill 复制到 Cursor skills 目录

安装完成后，**重启终端**以刷新环境变量。

### 第四步：在 Cursor 中使用

在 Cursor 中打开任意项目，对 Agent 说：

```
帮我把这个 B 站视频转成文字并生成摘要：https://www.bilibili.com/video/BV1TFcYzxEfK
```

Agent 会自动：
1. 检测环境是否就绪
2. 运行 `bvt.py` 脚本获取视频文本
3. 读取输出文件
4. **对原文做后处理**：添加标点、修正错别字、去除语气词、逻辑分段（见「Agent 后处理」）
5. 生成 2-4 句摘要并更新 `summary`
6. **删除原始视频**：转写完成后，若 output 目录或工作目录中存在下载的视频/音频文件（如 `.mp4`、`.webm`、`.mp3`、`.m4a`），删除以释放空间
7. 告诉你输出文件的位置

### 常见问题

**Q: 提示"没有字幕"怎么办？**

A: 很多 B 站视频没有上传 CC 字幕。可以：
- 加参数 `--cookies-from-browser safari`（Mac）或 `chrome`（Windows）使用浏览器 cookie
- 或安装 Whisper 进行语音转写：`pip install openai-whisper`

**Q: Whisper 转写很慢？**

A: 首次使用会下载模型（约 150MB），之后会快一些。长视频转写确实需要时间。

**Q: 在哪里找到输出文件？**

A: 默认在当前目录的 `output/` 文件夹，文件名为视频标题。

**Q: 后处理需要 API Key 吗？**

A: 不需要。使用 Cursor Agent 后处理时，由 Agent 直接对文本进行转换，无需配置 Gemini 等外部 API。

## 故障排查

详见 [reference.md](reference.md)。
