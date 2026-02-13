# B 站视频转文本 Skill - Windows 安装脚本
# 在 PowerShell 中以管理员身份运行

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  B 站视频转文本 Skill - 一键安装脚本 (Windows)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "警告：建议以管理员身份运行此脚本" -ForegroundColor Yellow
    Write-Host "某些安装步骤可能需要管理员权限" -ForegroundColor Yellow
    Write-Host ""
}

# 检测并安装 Chocolatey
Write-Host "检查 Chocolatey..." -ForegroundColor White
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "正在安装 Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    # 刷新环境变量
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "✓ Chocolatey 已安装" -ForegroundColor Green
}

# 检测并安装 Python
Write-Host ""
Write-Host "检查 Python..." -ForegroundColor White
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "正在安装 Python 3..." -ForegroundColor Yellow
    
    # 尝试用 winget（Windows 11）
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install --id Python.Python.3.12 -e --silent
    } else {
        # 使用 Chocolatey
        choco install python -y
    }
    
    # 刷新环境变量
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    $pythonVersion = python --version
    Write-Host "✓ Python 已安装: $pythonVersion" -ForegroundColor Green
}

# 检测并安装 ffmpeg
Write-Host ""
Write-Host "检查 ffmpeg..." -ForegroundColor White
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "正在安装 ffmpeg..." -ForegroundColor Yellow
    choco install ffmpeg -y
    
    # 刷新环境变量
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "✓ ffmpeg 已安装" -ForegroundColor Green
}

# 检测并安装 yt-dlp
Write-Host ""
Write-Host "检查 yt-dlp..." -ForegroundColor White
if (-not (Get-Command yt-dlp -ErrorAction SilentlyContinue)) {
    Write-Host "正在安装 yt-dlp..." -ForegroundColor Yellow
    python -m pip install --user yt-dlp
    
    # 刷新环境变量
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "✓ yt-dlp 已安装" -ForegroundColor Green
}

# 安装 Python 依赖
Write-Host ""
Write-Host "安装 Python 依赖..." -ForegroundColor White
python -m pip install --user -r requirements.txt
Write-Host "✓ Python 依赖安装完成" -ForegroundColor Green

# 复制 skill 到 Cursor skills 目录（可选）
Write-Host ""
$response = Read-Host "是否将此 skill 复制到 ~/.cursor/skills/？(y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    $skillDir = "$env:USERPROFILE\.cursor\skills\bilibili-video-to-text"
    New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\skills" | Out-Null
    
    # 如果已存在，先备份
    if (Test-Path $skillDir) {
        Write-Host "目录已存在，正在备份..." -ForegroundColor Yellow
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        Move-Item $skillDir "$skillDir.backup.$timestamp"
    }
    
    Copy-Item -Path (Get-Location) -Destination $skillDir -Recurse
    Write-Host "✓ Skill 已复制到 $skillDir" -ForegroundColor Green
}

# 运行环境检测
Write-Host ""
Write-Host "运行环境检测..." -ForegroundColor White
python scripts\check_env.py

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "✓ 安装完成！" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "接下来：" -ForegroundColor White
Write-Host "1. 重启 PowerShell 或 Cursor 终端（刷新环境变量）" -ForegroundColor White
Write-Host "2. 打开 Cursor（需要 Pro 会员）" -ForegroundColor White
Write-Host "3. 在 Cursor 中对 Agent 说：「帮我把这个 B 站视频转成文字并生成摘要：<视频链接>」" -ForegroundColor White
Write-Host ""
Write-Host "示例：" -ForegroundColor White
Write-Host '  "帮我把这个 B 站视频转成文字：https://www.bilibili.com/video/BV1TFcYzxEfK"' -ForegroundColor Cyan
Write-Host ""
Write-Host "注意：" -ForegroundColor Yellow
Write-Host "- 部分 B 站视频可能没有 CC 字幕" -ForegroundColor White
Write-Host "- 如需使用语音转写，请安装: pip install openai-whisper" -ForegroundColor White
Write-Host "- 首次使用 Whisper 会下载模型（约 150MB）" -ForegroundColor White
Write-Host ""
