#!/bin/bash
set -e

echo "================================================"
echo "  B 站视频转文本 Skill - 一键安装脚本"
echo "================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检测操作系统
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo -e "${RED}错误：不支持的操作系统 $OSTYPE${NC}"
    echo "请在 Mac 或 Linux 上运行此脚本，Windows 用户请使用 setup.ps1"
    exit 1
fi

echo -e "${GREEN}✓ 检测到操作系统: $OS${NC}"
echo ""

# 检测并安装 Homebrew (仅 Mac)
if [ "$OS" == "mac" ]; then
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}正在安装 Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # 添加 brew 到 PATH (Apple Silicon)
        if [ -d "/opt/homebrew/bin" ]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        echo -e "${GREEN}✓ Homebrew 已安装${NC}"
    fi
fi

# 检测并安装 Python
echo ""
echo "检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}正在安装 Python 3...${NC}"
    if [ "$OS" == "mac" ]; then
        brew install python@3.11
    else
        sudo apt-get update && sudo apt-get install -y python3 python3-pip
    fi
else
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓ Python 已安装: $PYTHON_VERSION${NC}"
fi

# 检测并安装 ffmpeg
echo ""
echo "检查 ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}正在安装 ffmpeg...${NC}"
    if [ "$OS" == "mac" ]; then
        brew install ffmpeg
    else
        sudo apt-get install -y ffmpeg
    fi
else
    echo -e "${GREEN}✓ ffmpeg 已安装${NC}"
fi

# 检测并安装 yt-dlp
echo ""
echo "检查 yt-dlp..."
if ! command -v yt-dlp &> /dev/null; then
    echo -e "${YELLOW}正在安装 yt-dlp...${NC}"
    if [ "$OS" == "mac" ]; then
        brew install yt-dlp
    else
        python3 -m pip install --user yt-dlp
    fi
else
    echo -e "${GREEN}✓ yt-dlp 已安装${NC}"
fi

# 安装 Python 依赖
echo ""
echo "安装 Python 依赖..."
python3 -m pip install --user -r requirements.txt
echo -e "${GREEN}✓ Python 依赖安装完成${NC}"

# 复制 skill 到 Cursor skills 目录（可选）
echo ""
read -p "是否将此 skill 复制到 ~/.cursor/skills/？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    SKILL_DIR="$HOME/.cursor/skills/bilibili-video-to-text"
    mkdir -p "$HOME/.cursor/skills"
    
    # 如果已存在，先备份
    if [ -d "$SKILL_DIR" ]; then
        echo -e "${YELLOW}目录已存在，正在备份...${NC}"
        mv "$SKILL_DIR" "$SKILL_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    cp -r "$(pwd)" "$SKILL_DIR"
    echo -e "${GREEN}✓ Skill 已复制到 $SKILL_DIR${NC}"
fi

# 运行环境检测
echo ""
echo "运行环境检测..."
python3 scripts/check_env.py

echo ""
echo "================================================"
echo -e "${GREEN}✓ 安装完成！${NC}"
echo "================================================"
echo ""
echo "接下来："
echo "1. 打开 Cursor（需要 Pro 会员）"
echo "2. 在 Cursor 中对 Agent 说：「帮我把这个 B 站视频转成文字并生成摘要：<视频链接>」"
echo ""
echo "示例："
echo '  "帮我把这个 B 站视频转成文字：https://www.bilibili.com/video/BV1TFcYzxEfK"'
echo ""
echo -e "${YELLOW}注意：${NC}"
echo "- 部分 B 站视频可能没有 CC 字幕"
echo "- 如需使用语音转写，请安装: pip install openai-whisper"
echo "- 首次使用 Whisper 会下载模型（约 150MB）"
echo ""
