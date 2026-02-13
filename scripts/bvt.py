#!/usr/bin/env python3
"""
Bilibili Video to Text (bvt): 从 B 站视频链接提取转录文本。
优先使用字幕，无字幕时下载视频并语音转写。
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# 修复 SSL 证书问题（适配代理/VPN 环境）
import ssl
import urllib.request

def fix_ssl_for_proxy():
    """修复代理/VPN 环境下的 SSL 证书问题"""
    try:
        # 尝试使用 certifi
        import certifi
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    except ImportError:
        pass
    
    # 创建不验证证书的 SSL 上下文（仅用于 Whisper 模型下载）
    ssl._create_default_https_context = ssl._create_unverified_context

# 在脚本开始时修复 SSL
fix_ssl_for_proxy()

# 脚本所在目录
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def extract_bv(url: str) -> str | None:
    """从 B 站 URL 提取 BV 号。"""
    if not url:
        return None
    url = url.strip()
    # BV1xx... 格式
    m = re.search(r"[Bb][Vv]([a-zA-Z0-9]+)", url)
    return m.group(0) if m else None


def is_bilibili_url(url: str) -> bool:
    return "bilibili.com" in url or re.search(r"[Bb][Vv][a-zA-Z0-9]+", url or "") is not None


def parse_srt(text: str) -> list[str]:
    """解析 SRT 字幕为文本行列表。"""
    lines = text.replace("\r\n", "\n").split("\n")
    segments = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r"^\d+$", line):
            continue
        if "-->" in line:
            continue
        segments.append(line)
    return segments


def parse_vtt(text: str) -> list[str]:
    """解析 VTT 字幕。"""
    lines = text.replace("\r\n", "\n").split("\n")
    segments = []
    for line in lines:
        line = line.strip()
        if not line or line == "WEBVTT":
            continue
        if line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line:
            continue
        if re.match(r"^(align|position|size|line):", line, re.I):
            continue
        line = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", line).strip()
        if line:
            segments.append(line)
    return segments


def parse_ass(text: str) -> list[str]:
    """解析 ASS 字幕，提取 Dialogue 行的文本。"""
    segments = []
    in_events = False
    for line in text.replace("\r\n", "\n").split("\n"):
        line = line.strip()
        if line.startswith("[Events]"):
            in_events = True
            continue
        if in_events and line.startswith("Dialogue:"):
            # Format: Start,End,Style,...,Text
            parts = line.split(",", 9)
            if len(parts) >= 10:
                raw = parts[9].strip()
                # 移除 {\...} 样式
                raw = re.sub(r"\{[^}]*\}", "", raw)
                if raw:
                    segments.append(raw)
    return segments


def parse_subtitle_file(path: str) -> list[str]:
    """根据扩展名解析字幕文件。"""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    ext = Path(path).suffix.lower()
    if ext == ".srt":
        return parse_srt(text)
    if ext == ".vtt":
        return parse_vtt(text)
    if ext == ".ass":
        return parse_ass(text)
    # 默认按 srt 尝试
    return parse_srt(text)


def postprocess_text(text: str, api_key: str | None) -> str:
    """后处理：标点、错别字、语气词、分段。"""
    try:
        sys.path.insert(0, str(SCRIPT_DIR))
        from postprocess import postprocess
        return postprocess(text, api_key)
    except ImportError:
        return text


def segments_to_paragraph(segments: list[str]) -> str:
    """将字幕片段合并为段落文本，去重、去噪。"""
    seen = set()
    cleaned = []
    for s in segments:
        s = re.sub(r"\s+", " ", s).strip()
        s = re.sub(r"\[[^\]]*\]", "", s).strip()
        s = re.sub(r"\{[^}]*\}", "", s).strip()
        if not s or s in seen:
            continue
        seen.add(s)
        cleaned.append(s)
    return " ".join(cleaned).replace("  ", " ").strip()


def run_cmd(cmd: list[str], cwd: str | None = None, timeout: int = 300) -> tuple[int, str]:
    """运行命令，返回 (exit_code, output)。"""
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
            timeout=timeout,
        )
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode, out.strip()
    except subprocess.TimeoutExpired:
        return -1, "Command timed out"
    except Exception as e:
        return -1, str(e)


def try_subtitles(
    url: str,
    lang: str = "zh-CN",
    cookies_from_browser: str | None = None,
) -> str | None:
    """
    尝试用 yt-dlp 拉取字幕。
    返回字幕文本，失败返回 None。
    B 站字幕通常需要登录，可传 cookies_from_browser='chrome' 等使用浏览器 cookie。
    """
    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        return None

    tmp = tempfile.mkdtemp(prefix="bvt-subs-")
    try:
        out_tpl = os.path.join(tmp, "%(id)s.%(ext)s")

        def build_cmd(sub_lang: str) -> list[str]:
            cmd = [
                ytdlp,
                "--write-sub",
                "--write-auto-sub",
                "--skip-download",
                "--sub-lang",
                sub_lang,
                "-o",
                out_tpl,
                "--no-warnings",
                url,
            ]
            if cookies_from_browser:
                cmd[1:1] = ["--cookies-from-browser", cookies_from_browser]
            return cmd

        # 尝试多种中文语言代码
        for l in [lang, "zh", "zh-Hans", "zh-CN", "zh-TW"]:
            code, _ = run_cmd(build_cmd(l), timeout=90)
            if code != 0:
                continue

            files = []
            for f in os.listdir(tmp):
                fp = os.path.join(tmp, f)
                if os.path.isfile(fp) and f.lower().endswith((".srt", ".vtt", ".ass")):
                    files.append(fp)

            if files:
                files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                try:
                    segments = parse_subtitle_file(files[0])
                    text = segments_to_paragraph(segments)
                    if text and len(text) > 50:
                        return text
                except Exception:
                    pass
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return None


def get_video_info(url: str) -> dict:
    """用 yt-dlp 获取视频元数据。"""
    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        return {"title": "", "duration": ""}

    code, out = run_cmd(
        [
            ytdlp,
            "--dump-json",
            "--no-download",
            "--no-warnings",
            url,
        ],
        timeout=30,
    )
    if code != 0 or not out:
        return {"title": "", "duration": ""}

    try:
        data = json.loads(out)
        duration = data.get("duration") or 0
        mins, secs = divmod(int(duration), 60)
        hrs, mins = divmod(mins, 60)
        if hrs > 0:
            dur_str = f"{hrs}:{mins:02d}:{secs:02d}"
        else:
            dur_str = f"{mins}:{secs:02d}"
        return {
            "title": (data.get("title") or "").strip(),
            "duration": dur_str,
        }
    except Exception:
        return {"title": "", "duration": ""}


def download_and_transcribe(url: str, tmp_dir: str) -> str | None:
    """下载视频、提取音频、Whisper 转写。"""
    ytdlp = shutil.which("yt-dlp")
    ffmpeg = shutil.which("ffmpeg")
    if not ytdlp or not ffmpeg:
        return None

    # 下载音频
    audio_path = os.path.join(tmp_dir, "audio.mp3")
    code, out = run_cmd(
        [
            ytdlp,
            "-x",
            "--audio-format",
            "mp3",
            "-o",
            os.path.join(tmp_dir, "audio.%(ext)s"),
            "--no-warnings",
            url,
        ],
        cwd=tmp_dir,
        timeout=600,
    )
    if code != 0:
        return None

    # 找到下载的音频文件
    audio_file = None
    for f in os.listdir(tmp_dir):
        if f.endswith((".mp3", ".m4a", ".webm")):
            audio_file = os.path.join(tmp_dir, f)
            break
    if not audio_file or not os.path.exists(audio_file):
        return None

    try:
        import whisper

        model = whisper.load_model("base")
        result = model.transcribe(audio_file, language="zh", fp16=False)
        return (result.get("text") or "").strip()
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="B站视频转文本")
    parser.add_argument("url", nargs="?", help="B站视频链接")
    parser.add_argument("--output-dir", "-o", default=".", help="输出目录")
    parser.add_argument("--lang", "-l", default="zh-CN", help="字幕语言")
    parser.add_argument(
        "--cookies-from-browser",
        metavar="BROWSER",
        help="从浏览器读取 cookie（B 站字幕需登录时使用，如 chrome/safari）",
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON 而非写入文件")
    parser.add_argument("--no-fallback", action="store_true", help="无字幕时不尝试 Whisper 转写")
    parser.add_argument(
        "--post-process",
        action="store_true",
        help="后处理：添加标点、修正错别字、去除语气词、逻辑分段（需 GEMINI_API_KEY）",
    )
    parser.add_argument(
        "--gemini-api-key",
        metavar="KEY",
        help="Gemini API Key，也可用环境变量 GEMINI_API_KEY",
    )
    args = parser.parse_args()

    url = args.url
    if not url:
        parser.print_help()
        sys.exit(1)

    if not is_bilibili_url(url):
        print("错误：请输入有效的 B 站视频链接", file=sys.stderr)
        sys.exit(1)

    # 获取元数据
    info = get_video_info(url)
    title = info.get("title") or "未知标题"
    duration = info.get("duration") or ""

    # 路径 A：尝试字幕
    text = try_subtitles(url, args.lang, args.cookies_from_browser)

    # 路径 B：无字幕时下载转写
    if not text and not args.no_fallback:
        tmp_dir = tempfile.mkdtemp(prefix="bvt-dl-")
        try:
            text = download_and_transcribe(url, tmp_dir)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    if not text or len(text.strip()) < 10:
        print("错误：未能获取视频文本（可能无字幕且 Whisper 转写失败）", file=sys.stderr)
        sys.exit(1)

    # 后处理：标点、错别字、语气词、分段
    if args.post_process:
        api_key = args.gemini_api_key or os.environ.get("GEMINI_API_KEY")
        if api_key:
            print("正在进行文本后处理（标点、错别字、语气词、分段）...", file=sys.stderr)
            text = postprocess_text(text, api_key)
        else:
            print("警告：未设置 GEMINI_API_KEY，跳过后处理", file=sys.stderr)

    # 输出
    result = {
        "title": title,
        "source": url,
        "source_type": "bilibili",
        "duration": duration,
        "text": text,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_title = re.sub(r'[<>:"/\\|?*]', "_", title)[:100]
    out_path = out_dir / f"{safe_title}.md"

    # 写入 MD，摘要留空由 Agent 填充
    content = f'''---
title: "{title.replace(chr(34), "'")}"
source: "{url}"
source_type: bilibili
duration: "{duration}"
processed_at: "{datetime.now().isoformat(timespec='seconds')}"
tags: []
summary: |
  （由 Agent 根据原文生成 2-4 句摘要）
---

# 完整原文

{text}
'''
    out_path.write_text(content, encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
