# B 站视频转文本 Skill

从 B 站视频链接提取完整转录文本并生成带 YAML 元数据的 Markdown 文件，便于知识库索引和笔记整理。

---

## 📦 Zip 安装（推荐）

如你通过 zip 包获得本 skill，请直接阅读 **[安装说明.md](安装说明.md)**。

在 Cursor 中打开本文件夹后，对 Agent 说：

> **帮我安装这个 B 站转文本 skill，按照「安装说明.md」里的 Agent 安装步骤执行**

Agent 会自动完成解压、移动、依赖安装和环境检查，你无需接触任何命令行。

---

## 功能

- 优先从 B 站视频提取 CC 字幕（无需下载完整视频）
- 无字幕时自动下载视频并语音转写（Whisper）
- 输出标准 Markdown，含 YAML frontmatter（title、source、duration、tags、summary）
- 支持 Obsidian、Notion 等知识库的标签与摘要

---

## 🚀 快速开始（教学版）

**适用对象：** Cursor 新手、零基础学生

### 三步上手

#### 1️⃣ 克隆项目

```bash
git clone https://github.com/<your-username>/bilibili-video-to-text.git ~/.cursor/skills/bilibili-video-to-text
cd ~/.cursor/skills/bilibili-video-to-text
```

如果提示找不到 `git` 命令，在 Cursor 中对 Agent 说：「帮我安装 Git」

#### 2️⃣ 一键安装

**Mac/Linux:**
```bash
./setup.sh
```

**Windows (PowerShell 管理员模式):**
```powershell
.\setup.ps1
```

脚本会自动安装所有依赖（Python、ffmpeg、yt-dlp 等），等待 2-5 分钟。

安装完成后**重启终端**。

#### 3️⃣ 开始使用

打开 Cursor（需要 Pro 会员），对 Agent 说：

```
帮我把这个 B 站视频转成文字并生成摘要：https://www.bilibili.com/video/BV1TFcYzxEfK
```

🎉 几分钟后，你会得到一个带摘要的 Markdown 笔记！

### 视频教程

[待补充：录制演示视频]

### 常见问题速查

- **"没有字幕"** → 安装 Whisper: `pip install openai-whisper`
- **"找不到命令"** → 重启终端刷新环境变量
- **"Agent 不响应"** → 确保 Cursor Pro 会员有效

更多问题见 [TEACHING.md](TEACHING.md)（教师指南）

---

## 📦 完整安装（进阶用户）

### 1. Clone 到 Cursor Skills

```bash
git clone https://github.com/<your-username>/bilibili-video-to-text.git ~/.cursor/skills/bilibili-video-to-text
```

### 2. 安装依赖

**Mac：**

```bash
brew install python ffmpeg
cd ~/.cursor/skills/bilibili-video-to-text
pip install -r requirements.txt
```

**Windows：**

```powershell
winget install Python.Python.3.12
choco install ffmpeg
cd %USERPROFILE%\.cursor\skills\bilibili-video-to-text
pip install -r requirements.txt
```

### 3. 环境检测

```bash
python scripts/check_env.py
```

若输出中 `ready_for_subtitle` 为 `true`，即可使用。

## 使用

### 在 Cursor 中

对 Agent 说：

> 帮我把这个 B 站视频转成文字并生成摘要：https://www.bilibili.com/video/BV1NfFdznE7s

Agent 会按本 skill 的流程执行，并生成带摘要的 MD 文件。

### 命令行

```bash
python scripts/bvt.py "https://www.bilibili.com/video/BV1NfFdznE7s" --output-dir ./output
```

若视频有 CC 字幕但需登录，可加 `--cookies-from-browser chrome`（或 safari）。

输出文件示例：`output/OpenClaw斩杀线：80%的应用消失....md`

### 参数

| 参数 | 说明 |
|------|------|
| `url` | B 站视频链接 |
| `--output-dir`, `-o` | 输出目录，默认当前目录 |
| `--lang`, `-l` | 字幕语言，默认 zh-CN |
| `--cookies-from-browser` | 从浏览器读取 cookie（B 站字幕需登录时使用） |
| `--json` | 输出 JSON 而非写入文件 |
| `--no-fallback` | 无字幕时不尝试 Whisper 转写 |

## 输出示例

```markdown
---
title: "OpenClaw斩杀线：80%的应用消失..."
source: "https://www.bilibili.com/video/BV1NfFdznE7s"
source_type: bilibili
duration: "47:01"
processed_at: "2025-02-12T16:00:00"
tags:
  - AI
  - OpenClaw
  - SaaS
summary: |
  本视频探讨 OpenClaw 等技术对应用生态的影响...（2-4 句摘要）
---

# 完整原文

[完整转录文本...]
```

## 📚 相关文档

- **[TEACHING.md](TEACHING.md)** - 教师使用指南（课堂演示、扩展练习）
- **[SKILL.md](SKILL.md)** - Skill 技术文档（触发条件、流程说明）
- **[reference.md](reference.md)** - 故障排查手册

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

---

**教学目标：** 让学生通过这个项目学会使用 Cursor AI 编程助手、命令行工具和 Python 项目管理。
