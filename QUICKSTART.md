# 快速开始指南

**⏱️ 预计用时：10 分钟**

## 适用场景

本指南适合：
- ✅ 首次使用 Cursor 的学生
- ✅ 想快速上手 AI 辅助工具的新手
- ✅ 需要从 B 站视频提取文字笔记的用户

## 前置条件

1. **Cursor IDE**：已安装 Cursor，并有 Pro 会员（或试用期）
2. **网络**：能访问 GitHub 和 B 站
3. **操作系统**：Mac、Windows 或 Linux

---

## 第一步：克隆项目（2 分钟）

### 打开 Cursor 终端

- **Mac/Linux**：按 `Ctrl + ~` 或菜单 → Terminal → New Terminal
- **Windows**：同上

### 执行克隆命令

```bash
git clone https://github.com/<your-username>/bilibili-video-to-text.git ~/.cursor/skills/bilibili-video-to-text
```

如果提示 `git: command not found`，在 Cursor 中对 Agent 说：

```
请帮我安装 Git
```

Agent 会自动检测你的操作系统并给出安装指令。

---

## 第二步：运行安装脚本（5 分钟）

### 进入项目目录

```bash
cd ~/.cursor/skills/bilibili-video-to-text
```

### 运行一键安装

**Mac/Linux：**

```bash
chmod +x setup.sh
./setup.sh
```

**Windows（以管理员身份打开 PowerShell）：**

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup.ps1
```

### 等待安装完成

脚本会自动：
1. 检测操作系统
2. 安装 Homebrew（Mac）或 Chocolatey（Windows）
3. 安装 Python 3.10+
4. 安装 ffmpeg
5. 安装 yt-dlp
6. 安装 Python 依赖包
7. 运行环境检测

看到 `✓ 安装完成！` 即成功。

### 重要：重启终端

安装完成后，**关闭并重新打开终端**，刷新环境变量。

---

## 第三步：开始使用（3 分钟）

### 在 Cursor 中打开 Agent 对话

- 按 `Cmd + L`（Mac）或 `Ctrl + L`（Windows）
- 或点击右上角的聊天图标

### 输入指令

```
帮我把这个 B 站视频转成文字并生成摘要：https://www.bilibili.com/video/BV1TFcYzxEfK
```

### 等待处理

Agent 会：
1. 读取 `SKILL.md` 理解任务
2. 运行 `check_env.py` 检测环境
3. 执行 `bvt.py` 提取视频文本
4. 用 AI 生成 2-4 句摘要
5. 创建 Markdown 文件

### 查看结果

Agent 会告诉你输出文件的位置，例如：

```
✅ 已生成笔记：/path/to/output/验证码.md
```

打开文件，你会看到：

```markdown
---
title: "验证码"
source: "https://www.bilibili.com/video/BV1TFcYzxEfK"
duration: "0:15"
tags:
  - 测试
summary: |
  这是视频的核心内容摘要...
---

# 完整原文

[完整的转录文本]
```

---

## 常见问题

### ❓ 提示"视频没有字幕"

**原因：** 很多 B 站视频没有上传 CC 字幕。

**解决方案 1（推荐）：** 换一个有字幕的视频

**解决方案 2：** 安装 Whisper 进行语音转写

```bash
pip install openai-whisper
```

然后再次运行命令（不加 `--no-fallback`）。

### ❓ Agent 不响应或报错

**检查清单：**
- [ ] 确认 Cursor Pro 会员有效
- [ ] 重启了终端/Cursor
- [ ] 网络连接正常
- [ ] 视频链接正确

### ❓ 找不到命令（command not found）

**原因：** 环境变量未刷新。

**解决：** 重启终端或 Cursor。

如果问题仍然存在，手动添加到 PATH：

**Mac:**
```bash
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
系统设置 → 环境变量 → 编辑 Path → 添加 Python 和 ffmpeg 路径

---

## 下一步

### 📚 深入学习

- 阅读 [SKILL.md](SKILL.md) 了解技术细节
- 阅读 [TEACHING.md](TEACHING.md)（教师参考）
- 查看 [reference.md](reference.md) 排查问题

### 🎯 扩展练习

1. **批量处理**：找 3-5 个短视频，批量生成笔记
2. **自定义摘要**：修改提示词，生成不同风格的摘要
3. **知识库整理**：将生成的 MD 文件导入 Obsidian/Notion

### 🤝 参与贡献

- 在 GitHub 提 Issue 报告问题
- 提交 Pull Request 改进代码
- 分享你的使用心得

---

**恭喜！你已经掌握了用 AI 辅助工具提取视频笔记的技能。🎉**

有问题？查看 [TEACHING.md](TEACHING.md) 或在 GitHub Issues 提问。
