# B 站视频转文本 Skill

从 B 站视频链接提取完整转录文本并生成带 YAML 元数据的 Markdown 文件，便于知识库索引和笔记整理。

---

## 平台支持

| 平台 | AI 授权 |
|------|---------|
| **Cursor** | Cursor Agent（需 Cursor Pro） |
| **OpenClaw** | OpenClaw 模型（按 OpenClaw 配置） |

**无需单独配置 API**，后处理与摘要由各自平台的 Agent 完成。

---

## 📦 Zip 安装（推荐）

如你通过 zip 包获得本 skill，请直接阅读 **[安装说明.md](安装说明.md)**。

在 Cursor 或 OpenClaw 中打开本文件夹后，对 Agent 说：

> **帮我安装这个 B 站转文本 skill，按照「安装说明.md」里的 Agent 安装步骤执行**

Agent 会自动完成解压、移动、依赖安装和环境检查，你无需接触任何命令行。

---

## 功能

- 优先从 B 站视频提取 CC 字幕（无需下载完整视频）
- 无字幕时自动下载视频并语音转写（Whisper）
- 输出标准 Markdown，含 YAML frontmatter（title、source、duration、tags、summary）
- 支持 Obsidian、Notion 等知识库的标签与摘要

---

## 🚀 快速开始

### Cursor 用户

```bash
git clone https://github.com/AAAAAAlone/skills.git ~/.cursor/skills/bilibili-video-to-text
cd ~/.cursor/skills/bilibili-video-to-text
./setup.sh
```

安装完成后重启终端，对 Agent 说：「帮我把这个 B 站视频转成文字并生成摘要：<视频链接>」

### OpenClaw 用户

```bash
git clone https://github.com/AAAAAAlone/skills.git ~/.openclaw/skills/bilibili-video-to-text
cd ~/.openclaw/skills/bilibili-video-to-text
./setup.sh
```

安装完成后，对 OpenClaw Agent 说：「帮我把这个 B 站视频转成文字并生成摘要：<视频链接>」

### Windows

在 PowerShell 中运行 `.\setup.ps1`，路径对应改为 `%USERPROFILE%\.cursor\skills\bilibili-video-to-text` 或 `%USERPROFILE%\.openclaw\skills\bilibili-video-to-text`。

### 常见问题速查

- **"没有字幕"** → 安装 Whisper: `pip install openai-whisper`
- **"找不到命令"** → 重启终端刷新环境变量
- **"Agent 不响应"** → Cursor 确认 Pro 会员有效；OpenClaw 确认模型已授权

更多问题见 [TEACHING.md](TEACHING.md)（教师指南）、[reference.md](reference.md)（故障排查）

---

## 使用

### 在 Cursor / OpenClaw 中

对 Agent 说：

> 帮我把这个 B 站视频转成文字并生成摘要：https://www.bilibili.com/video/BV1NfFdznE7s

Agent 会按本 skill 的流程执行，并生成带摘要的 MD 文件。后处理与摘要由平台 Agent 完成，无需额外 API。

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
