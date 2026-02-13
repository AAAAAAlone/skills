---
name: bilibili-video-to-text
description: 从 B 站视频链接获取转录文本。流程：bvt.py 转写 → Agent 必须对原文做后处理（添加标点、修正错别字、去除语气词、逻辑分段）→ 生成 2-4 句摘要。优先提取字幕，无字幕时 Whisper 转写。使用场景：bilibili.com 链接、转文字、要摘要、要后处理。
---

# B 站视频转文本

> **执行须知**：转写完成后，Agent **必须**对原文执行后处理（标点、错别字、语气词、分段），再生成摘要。不可跳过。

## 平台与授权（默认方式）

本 skill 支持两种平台，**AI 能力均由各自平台提供，无需单独配置 API**：

| 平台 | AI 授权方式 |
|------|-------------|
| **Cursor** | 使用 Cursor Agent（需 Cursor Pro） |
| **OpenClaw** | 使用 OpenClaw 的模型授权（API Key / OAuth 等，按 OpenClaw 配置） |

后处理、摘要生成均由**当前平台的 Agent** 完成，用户只需在对应平台完成授权即可。

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
3. **执行转写**（**不传** `--post-process`，后处理由平台 Agent 完成）：

```bash
python scripts/bvt.py "https://www.bilibili.com/video/BVxxxxx" --output-dir <输出目录>
```

若 B 站视频有 CC 字幕但需登录，可加 `--cookies-from-browser chrome` 或 `safari`。

4. **后处理（必须）**：读取输出文件中 `# 完整原文` 下的正文，执行：添加标点、修正错别字、去除语气词、按逻辑分段；用处理后的文本替换原文
5. **生成摘要**：根据后处理后的原文，生成 2–4 句摘要，替换 YAML 中 `summary:` 的占位符
6. **可选 tags**：根据视频标题和内容，在 YAML 中补充 `tags` 数组
7. **删除原始视频**：转写完成后，若 output 目录或工作目录中存在下载的视频/音频文件（`.mp4`、`.webm`、`.mp3`、`.m4a`），删除以释放空间

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

### Cursor 用户

1. **安装 Cursor**：从 https://cursor.sh 下载并安装（需要 Pro 会员）
2. **安装 skill**：按 [安装说明.md](安装说明.md) 执行，或对 Agent 说「帮我安装这个 B 站转文本 skill」
3. **使用**：对 Agent 说「帮我把这个 B 站视频转成文字并生成摘要：<视频链接>」

### OpenClaw 用户

1. **安装 OpenClaw**：按 OpenClaw 官方文档完成安装与模型授权
2. **安装 skill**：`clawdhub install bilibili-video-to-text` 或复制到 `~/.openclaw/skills/bilibili-video-to-text`
3. **使用**：对 OpenClaw Agent 说「帮我把这个 B 站视频转成文字并生成摘要：<视频链接>」

AI 后处理与摘要由 OpenClaw 的模型完成，无需额外配置 API。

### 通用安装（Mac/Linux）

```bash
# Cursor：克隆到 Cursor skills 目录
git clone https://github.com/AAAAAAlone/skills.git ~/.cursor/skills/bilibili-video-to-text
cd ~/.cursor/skills/bilibili-video-to-text

# OpenClaw：克隆到 OpenClaw skills 目录
# git clone https://github.com/AAAAAAlone/skills.git ~/.openclaw/skills/bilibili-video-to-text
# cd ~/.openclaw/skills/bilibili-video-to-text

# 运行安装脚本
./setup.sh
```

**Windows**：在 PowerShell 中运行 `.\setup.ps1`

安装完成后**重启终端**。

### 流程说明（Cursor / OpenClaw 通用）

Agent 必须执行：
1. 检测环境是否就绪
2. 运行 `bvt.py` 脚本获取视频文本（不传 `--post-process`）
3. 读取输出文件
4. **对原文做后处理**（不可跳过）：添加标点、修正错别字、去除语气词、逻辑分段。用处理后的文本替换 `# 完整原文` 下的内容
5. 生成 2-4 句摘要并更新 `summary`
6. **删除原始视频**：转写完成后删除临时视频/音频文件
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

**Q: 需要单独配置 API Key 吗？**

A: 不需要。Cursor 使用 Cursor Agent；OpenClaw 使用 OpenClaw 的模型授权。AI 能力由各自平台提供。

## 故障排查

详见 [reference.md](reference.md)。
