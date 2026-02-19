"""
单格封面视觉判断：是否出现宝宝/儿童、人物气质是否偏宝妈、是否出现母婴用品等。
供 Vision API（OpenAI / Gemini / Claude）使用，返回结构化得分与置信度。
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

# 单格封面判断的系统与用户 Prompt（类型 + 调性 + 母婴场景细化）
COVER_JUDGE_SYSTEM = """你是一个抖音达人主页封面分析助手。给定一张视频封面的截图，请从以下维度打分并给出置信度。本评估用于母婴奶粉等推广，需区分「真实宝妈、0-3岁小宝宝、生活化」与「杂乱广告感、大龄儿童、AI/军装等」。

维度一：达人类型（是否宝妈 / 婴幼儿是否合适）
- 封面是否出现婴儿、儿童、孕妇（是/否，置信度 0-1）
- **婴幼儿年龄**：若出现儿童，请判断是否约为 **0-3 岁小宝宝**（婴儿、学步期、幼童）。若孩子明显为学龄或更大，则标为 false。字段 child_age_0_3: true/false, child_age_0_3_confidence: 0-1
- 画面中人物气质与穿搭是否偏「宝妈」（成熟、居家、亲子感为正向；过年轻、夜店风、纯娱乐/军装/AI 炫技等为负向）（1-10 分，置信度 0-1）
- 是否出现母婴/婴童用品（奶瓶、婴儿车、纸尿裤、教辅、儿童玩具等）（是/否，置信度 0-1）

维度二：调性（真实生活感 vs 杂乱/广告感）
- 封面是否**杂乱、广告感强、不真实**（多品牌堆砌、硬广感、像什么广告都接）？若是则调性不符。字段 cover_cluttered_or_ad_like: true/false, confidence 0-1
- 背景是否为**真实居家/生活化场景**（家庭、户外日常、非棚拍炫技）？字段 real_home_life_scene: true/false, confidence 0-1
- 是否使用**AI军装、AI创作、活跃女性滤镜**等与真实宝妈无关的风格？字段 ai_army_or_filter: true/false, confidence 0-1
- 在偏宝妈基础上，是否有「精致」感：美妆、穿搭、生活品质、女性健康等（1-10 分，置信度 0-1）

请严格按 JSON 输出，不要其他文字。格式如下（所有字段均需输出）：
{
  "has_baby_or_child": true/false,
  "has_baby_confidence": 0.0-1.0,
  "child_age_0_3": true/false,
  "child_age_0_3_confidence": 0.0-1.0,
  "person_mom_like_score": 1-10,
  "person_mom_confidence": 0.0-1.0,
  "has_maternal_products": true/false,
  "maternal_confidence": 0.0-1.0,
  "cover_cluttered_or_ad_like": true/false,
  "cover_cluttered_confidence": 0.0-1.0,
  "real_home_life_scene": true/false,
  "real_home_confidence": 0.0-1.0,
  "ai_army_or_filter": true/false,
  "ai_army_confidence": 0.0-1.0,
  "tone_refined_score": 1-10,
  "tone_refined_confidence": 0.0-1.0,
  "brief_reason": "一句话理由"
}
"""

COVER_JUDGE_USER_TEMPLATE = """请对这张抖音视频封面图按上述维度打分（重点：婴幼儿是否0-3岁、封面是否杂乱/广告感、是否真实居家场景、是否AI军装等），并输出完整 JSON。"""


def image_to_base64_data_uri(image_path: Union[str, Path], mime: str = "image/jpeg") -> str:
    path = Path(image_path)
    raw = path.read_bytes()
    b64 = base64.standard_b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


def describe_cover_with_vision(
    image_path: Union[str, Path],
    api_client: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    system_prompt: str = COVER_JUDGE_SYSTEM,
    user_prompt: str = COVER_JUDGE_USER_TEMPLATE,
) -> Dict[str, Any]:
    image_path = Path(image_path)
    if not image_path.exists():
        return {"error": f"file not found: {image_path}", "raw": None}
    data_uri = image_to_base64_data_uri(image_path)
    if api_client == "openai":
        return _call_openai_vision(data_uri, model=model, api_key=api_key, system_prompt=system_prompt, user_prompt=user_prompt)
    if api_client == "gemini":
        return _call_gemini_vision(image_path, model=model, api_key=api_key, system_prompt=system_prompt, user_prompt=user_prompt)
    if api_client == "anthropic":
        return _call_anthropic_vision(data_uri, model=model, api_key=api_key, system_prompt=system_prompt, user_prompt=user_prompt)
    return {"error": f"unknown api_client: {api_client}", "raw": None}


def _call_openai_vision(data_uri: str, model: Optional[str] = None, api_key: Optional[str] = None, system_prompt: str = COVER_JUDGE_SYSTEM, user_prompt: str = COVER_JUDGE_USER_TEMPLATE) -> Dict[str, Any]:
    try:
        from openai import OpenAI
    except ImportError:
        return {"error": "openai not installed", "raw": None}
    client = OpenAI(api_key=api_key)
    model = model or "gpt-4o"
    content = [{"type": "text", "text": user_prompt}, {"type": "image_url", "image_url": {"url": data_uri}}]
    try:
        resp = client.chat.completions.create(model=model, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": content}], max_tokens=1024)
        text = (resp.choices[0].message.content or "").strip()
        return _parse_cover_json(text)
    except Exception as e:
        return {"error": str(e), "raw": None}


def _call_gemini_vision(image_path: Path, model: Optional[str] = None, api_key: Optional[str] = None, system_prompt: str = COVER_JUDGE_SYSTEM, user_prompt: str = COVER_JUDGE_USER_TEMPLATE) -> Dict[str, Any]:
    try:
        import google.generativeai as genai
    except ImportError:
        return {"error": "google-generativeai not installed", "raw": None}
    if api_key:
        genai.configure(api_key=api_key)
    model_name = model or "gemini-1.5-flash"
    try:
        gen_model = genai.GenerativeModel(model_name)
        with open(image_path, "rb") as f:
            img_data = f.read()
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        resp = gen_model.generate_content([full_prompt, {"mime_type": "image/jpeg", "data": img_data}])
        text = (resp.text or "").strip()
        return _parse_cover_json(text)
    except Exception as e:
        return {"error": str(e), "raw": None}


def _call_anthropic_vision(data_uri: str, model: Optional[str] = None, api_key: Optional[str] = None, system_prompt: str = COVER_JUDGE_SYSTEM, user_prompt: str = COVER_JUDGE_USER_TEMPLATE) -> Dict[str, Any]:
    try:
        from anthropic import Anthropic
    except ImportError:
        return {"error": "anthropic not installed", "raw": None}
    import re
    client = Anthropic(api_key=api_key)
    model_name = model or "claude-sonnet-4-20250514"
    m = re.match(r"data:([^;]+);base64,(.+)", data_uri)
    if not m:
        return {"error": "invalid data_uri", "raw": None}
    b64 = m.group(2)
    media_type = "image/jpeg"
    try:
        resp = client.messages.create(model=model_name, max_tokens=1024, system=system_prompt, messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}, {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}}]}])
        text = resp.content[0].text if resp.content else ""
        return _parse_cover_json(text)
    except Exception as e:
        return {"error": str(e), "raw": None}


def _parse_cover_json(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"raw": text}
    if not text:
        return out
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        start = 1 if lines[0].startswith("```json") else 0
        end = next((i for i, l in enumerate(lines) if i > 0 and l.strip() == "```"), len(lines))
        text = "\n".join(lines[start:end])
    try:
        parsed = json.loads(text)
        for k, v in parsed.items():
            out[k] = v
    except json.JSONDecodeError:
        pass
    return out
