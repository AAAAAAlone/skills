#!/usr/bin/env python3
"""
文本后处理：标点恢复、错别字修正、语气词去除、逻辑分段。
支持 Gemini API（推荐）或规则兜底。
"""

import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def postprocess_with_gemini(raw_text: str, api_key: str | None = None) -> str | None:
    """
    使用 Gemini API 将口语文本转为结构化书面语。
    添加标点、修正错别字、去除语气词、按逻辑分段。
    """
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        import requests
    except ImportError:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    prompt = """请将以下口语转写文本转为规范的书面语，要求：
1. 添加正确的标点符号（逗号、句号、问号等）
2. 修正明显的错别字和同音字错误
3. 去除语气词和口头禅（如：啊、呢、嗯、好、完了、听我说、这个这个、那个那个、好吧、就是说 等）
4. 按语义逻辑分段，每段 2-4 句话，段与段之间空一行
5. 保持原意不变，只做格式和语言规范化
6. 直接输出处理后的文本，不要添加任何说明或前缀

原文：
"""
    payload = {
        "contents": [{"parts": [{"text": prompt + raw_text}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 8192,
        },
    }

    try:
        r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
        if r.status_code != 200:
            return None
        data = r.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text.strip()
    except Exception:
        return None


def postprocess_rule_based(raw_text: str) -> str:
    """
    规则兜底：基础语气词去除、简单分段。
    无 API 时使用，效果有限。
    """
    text = raw_text.strip()

    # 常见语气词/口头禅（保留语义的如「好」在句首可能是有意义的，这里做保守处理）
    fillers = [
        r"\s*啊\s*", r"\s*呢\s*", r"\s*嗯\s*", r"\s*哈\s*", r"\s*哦\s*",
        r"\s*好吧\s*", r"\s*完了\s*", r"\s*听我说\s*", r"\s*就是说\s*",
        r"这个这个", r"那个那个", r"\s*然后呢\s*", r"\s*那么\s*",
    ]
    for p in fillers:
        text = re.sub(p, " ", text)

    # 合并多余空格
    text = re.sub(r"\s+", " ", text).strip()

    # 简单分段：每约 80 字或遇到句末词（如「吧」「吗」「呢」后）分段
    # 这里简化：按固定长度分段
    chunks = []
    chunk_size = 100
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i : i + chunk_size])
    return "\n\n".join(chunks)


def postprocess(text: str, api_key: str | None = None) -> str:
    """
    主入口：优先 Gemini，失败则规则兜底。
    """
    result = postprocess_with_gemini(text, api_key)
    if result:
        return result
    return postprocess_rule_based(text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python postprocess.py <原始文本文件> [--api-key KEY]")
        sys.exit(1)

    path = Path(sys.argv[1])
    api_key = None
    if "--api-key" in sys.argv:
        idx = sys.argv.index("--api-key")
        if idx + 1 < len(sys.argv):
            api_key = sys.argv[idx + 1]

    raw = path.read_text(encoding="utf-8")
    out = postprocess(raw, api_key)
    print(out)
