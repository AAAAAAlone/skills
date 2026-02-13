---
title: "验证码"
source: "https://www.bilibili.com/video/BV1TFcYzxEfK"
source_type: bilibili
duration: "0:15"
processed_at: "2025-02-12T18:30:00"
tags:
  - 测试
  - 示例
summary: |
  这是一个测试视频的示例输出。实际使用时，Cursor Agent 会根据视频内容自动生成 2-4 句摘要，
  概括视频的核心内容、主要观点和适用场景。
---

# 完整原文

[由于测试视频没有 CC 字幕，这里展示的是模拟输出格式]

当 B 站视频有字幕时，这里会显示从字幕中提取并清理后的完整文本。文本会按自然段落组织，去除重复和无意义的内容。

如果视频没有字幕，且安装了 Whisper，则会显示语音识别转写的文本。Whisper 支持中文、英文等多种语言，转写准确率较高。

实际使用示例：

1. 在 Cursor 中打开任意项目
2. 按 Cmd/Ctrl + L 打开 Agent 对话
3. 输入：「帮我把这个 B 站视频转成文字并生成摘要：<视频链接>」
4. 等待 Agent 完成处理
5. Agent 会告诉你输出文件的位置

输出的 Markdown 文件可以直接导入到 Obsidian、Notion 等笔记工具，YAML frontmatter 中的 tags 和 summary 便于检索和管理。
