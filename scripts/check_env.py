#!/usr/bin/env python3
"""
环境检测脚本：检测 B 站视频转文本所需的依赖。
输出 JSON 格式，便于 Agent 解析并根据缺失项给出安装命令。
"""

import json
import platform
import shutil
import subprocess
import sys


def get_os():
    """检测操作系统。"""
    system = platform.system().lower()
    if system == "darwin":
        return "mac"
    if system == "windows":
        return "windows"
    return "linux"


def check_python():
    """检测 Python 版本，需 3.10+。"""
    v = sys.version_info
    ok = v.major >= 3 and v.minor >= 10
    return {
        "ok": ok,
        "version": f"{v.major}.{v.minor}.{v.micro}",
        "required": "3.10+",
    }


def check_cmd(cmd, version_arg="-v"):
    """检测命令是否存在。version_arg 可能是 -v, --version 等。"""
    path = shutil.which(cmd)
    if not path:
        return {"ok": False, "path": None, "version": None}
    try:
        r = subprocess.run(
            [cmd, version_arg] if version_arg else [cmd],
            capture_output=True,
            text=True,
            timeout=5,
        )
        out = (r.stdout or r.stderr or "").strip()
        # 取第一行作为版本信息
        first_line = out.split("\n")[0] if out else ""
        return {"ok": True, "path": path, "version": first_line[:80]}
    except Exception as e:
        return {"ok": False, "path": path, "version": None, "error": str(e)}


def check_ffmpeg():
    return check_cmd("ffmpeg", "-version")


def check_ytdlp():
    return check_cmd("yt-dlp", "--version")


def check_whisper():
    """检测 Whisper 是否可用（用于无字幕时的语音转写）。"""
    try:
        import whisper  # noqa: F401

        return {"ok": True, "path": "whisper (imported)", "version": "installed"}
    except ImportError:
        return {"ok": False, "path": None, "version": None}


def get_install_commands(os_type, results):
    """根据检测结果生成安装命令。"""
    cmds = []
    r = results

    if not r["python"]["ok"]:
        if os_type == "mac":
            cmds.append("brew install python")
        elif os_type == "windows":
            cmds.append("winget install Python.Python.3.12")
            cmds.append("# 或从 https://www.python.org/downloads/ 下载安装，勾选 Add to PATH")
        else:
            cmds.append("请安装 Python 3.10+: https://www.python.org/downloads/")

    if not r["ffmpeg"]["ok"]:
        if os_type == "mac":
            cmds.append("brew install ffmpeg")
        elif os_type == "windows":
            cmds.append("choco install ffmpeg")
            cmds.append("# 或从 https://www.gyan.dev/ffmpeg/builds/ 下载")
        else:
            cmds.append("请安装 ffmpeg: https://ffmpeg.org/download.html")

    if not r["yt_dlp"]["ok"]:
        if r["python"]["ok"]:
            cmds.append("pip install yt-dlp")
        else:
            if os_type == "mac":
                cmds.append("brew install yt-dlp")
            elif os_type == "windows":
                cmds.append("# 从 https://github.com/yt-dlp/yt-dlp/releases 下载 yt-dlp.exe 并加入 PATH")
            else:
                cmds.append("pip install yt-dlp  # 需先安装 Python")

    if not r["whisper"]["ok"] and r["python"]["ok"]:
        cmds.append("pip install openai-whisper  # 仅无字幕视频需要")

    return cmds


def main():
    os_type = get_os()
    results = {
        "os": os_type,
        "python": check_python(),
        "ffmpeg": check_ffmpeg(),
        "yt_dlp": check_ytdlp(),
        "whisper": check_whisper(),
    }

    # 计算是否满足基本需求（字幕路径只需 python + ffmpeg + yt-dlp）
    basic_ok = (
        results["python"]["ok"]
        and results["ffmpeg"]["ok"]
        and results["yt_dlp"]["ok"]
    )
    results["ready_for_subtitle"] = basic_ok
    results["ready_for_whisper"] = basic_ok and results["whisper"]["ok"]

    install_cmds = get_install_commands(os_type, results)
    results["install_commands"] = install_cmds
    results["all_ready"] = basic_ok

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
