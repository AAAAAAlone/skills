# B 站视频转文本 - 教师使用指南

## 教学目标

通过本 skill 的实践，学生将学会：

1. **使用 Cursor AI 编程助手**：理解如何通过自然语言与 AI 协作完成任务
2. **命令行基础**：熟悉终端、Git、Shell 脚本等基本工具
3. **Python 项目结构**：了解一个完整 Python 项目的组织方式
4. **依赖管理**：理解如何安装和管理项目依赖
5. **实用技能**：获得从视频中提取文本、整理知识库的实用能力

## 课堂演示流程（45 分钟）

### 第一部分：引入（5 分钟）

1. **展示痛点**：手动记录视频笔记的低效
2. **展示成果**：一条命令自动生成带摘要的 Markdown 笔记
3. **说明技术栈**：Python + yt-dlp + Whisper + Cursor AI

### 第二部分：环境准备（10 分钟）

**投屏演示：**

```bash
# 1. 克隆项目
git clone https://github.com/<your-repo>/bilibili-video-to-text.git ~/.cursor/skills/bilibili-video-to-text

# 2. 进入目录
cd ~/.cursor/skills/bilibili-video-to-text

# 3. 运行安装脚本
./setup.sh
```

**关键讲解点：**
- Git clone 的作用
- Shell 脚本如何自动化安装流程
- `~/.cursor/skills/` 目录的意义

### 第三部分：实战操作（20 分钟）

**选择一个 3-5 分钟的 B 站技术视频**（建议提前找好有字幕的）

**在 Cursor 中演示：**

1. 打开 Cursor，新建或打开项目
2. 按 `Cmd/Ctrl + L` 打开 Agent 对话
3. 输入：「帮我把这个 B 站视频转成文字并生成摘要：<视频链接>」
4. **边等待边讲解**：Agent 如何理解指令、调用脚本、生成摘要
5. 查看输出的 Markdown 文件

**强调：**
- Cursor Pro 会员的必要性（提供 AI 能力）
- Agent 如何读取 SKILL.md 指令
- 摘要是 AI 生成的，不是脚本写死的

### 第四部分：原理讲解（10 分钟）

**打开关键文件讲解架构：**

1. **SKILL.md**：告诉 Cursor Agent 这个 skill 是做什么的
2. **scripts/check_env.py**：如何检测系统环境
3. **scripts/bvt.py**：核心逻辑
   - 字幕优先策略
   - Whisper 兜底
   - YAML 元数据生成

**画图说明双路径：**

```
B站视频链接
    ↓
有字幕? → 是 → yt-dlp 拉取 → 解析 → 输出文本
    ↓ 否
下载视频 → 提取音频 → Whisper 转写 → 输出文本
    ↓
Agent 读取 → 生成摘要 → 更新 MD 文件
```

## 学生常见问题及解决方案

### 1. "我的电脑没装 Python"

**解决：** setup.sh 会自动安装。如果失败：
- Mac: `brew install python`
- Windows: 从 python.org 下载安装包

### 2. "提示找不到 yt-dlp"

**原因：** 环境变量未刷新

**解决：** 重启终端或 Cursor

### 3. "视频转写失败"

**可能原因：**
- 视频没有字幕且未安装 Whisper
- 网络问题无法访问 B 站

**解决：**
- 安装 Whisper: `pip install openai-whisper`
- 换一个有字幕的视频
- 使用 `--cookies-from-browser` 参数

### 4. "摘要生成不准确"

**原因：** Cursor Agent 理解有偏差

**解决：** 
- 更明确的指令：「用 3 句话总结视频核心内容」
- 让学生尝试改进 prompt，理解如何与 AI 沟通

### 5. "Mac M1/M2 芯片运行 Whisper 报错"

**解决：** 
```bash
pip uninstall openai-whisper
pip install openai-whisper --no-cache-dir
```

## 扩展练习建议

### 练习 1：批量处理（初级）

让学生修改脚本，支持从文本文件读取多个链接并批量处理。

**提示：** 在 `bvt.py` 中添加 `--batch` 参数。

### 练习 2：自定义摘要模板（中级）

让学生修改 SKILL.md 中的摘要生成指令，要求：
- 摘要包含「适合人群」
- 列出「关键要点」（3-5 条）

### 练习 3：添加时间戳（高级）

改进脚本，在输出的 Markdown 中保留字幕的时间戳，方便跳转。

**提示：** 修改 `parse_subtitle_file` 函数。

### 练习 4：构建自己的 Skill（进阶）

让学生基于此项目创建自己的 Cursor Skill，例如：
- YouTube 视频转文本
- 播客音频转文本
- PDF 转 Markdown

## 教学资源

### 推荐阅读

- [Cursor 官方文档](https://docs.cursor.sh)
- [yt-dlp 文档](https://github.com/yt-dlp/yt-dlp)
- [Whisper 模型说明](https://github.com/openai/whisper)

### 示例视频推荐

寻找以下特点的 B 站视频作为演示素材：
- 3-5 分钟长度
- 有 CC 字幕
- 技术或教程类内容
- 普通话清晰

### 课后作业建议

1. 用本工具处理 3 个不同类型的视频
2. 整理成 Markdown 笔记库
3. 写一篇「如何用 AI 提升学习效率」的反思

## 注意事项

### 版权提醒

**务必强调：**
- 转录文本仅供个人学习使用
- 不得用于商业用途
- 尊重原创作者版权

### Cursor Pro 会员

- 本 skill 依赖 Cursor Pro 的 AI 能力生成摘要
- 学生需要订阅 Cursor Pro（或使用试用期）
- 如果学校/机构购买，可申请教育优惠

### 网络问题

- B 站视频在某些地区可能需要代理
- yt-dlp 首次运行会下载依赖
- Whisper 模型约 150MB，需要稳定网络

## 教学效果评估

### 评估标准

1. **技能掌握**（60%）
   - 能独立安装和使用本 skill
   - 理解双路径策略
   - 能排查常见错误

2. **扩展能力**（30%）
   - 能修改参数优化输出
   - 能根据需求改进 prompt
   - 能迁移到其他场景

3. **协作意识**（10%）
   - 理解如何与 AI 协作
   - 知道何时求助文档/社区

### 成功标志

学生能够：
- ✅ 在 10 分钟内完成从安装到生成第一个笔记
- ✅ 解释 SKILL.md 的作用
- ✅ 独立解决 1-2 个常见问题
- ✅ 产出至少 3 篇视频笔记

## 联系与反馈

如果在教学过程中遇到问题或有改进建议，欢迎：
- 在 GitHub 提 Issue
- 通过邮件联系维护者
- 参与社区讨论

---

**祝教学顺利！希望学生们能通过这个项目感受到 AI 辅助编程的魅力。**
