"""
将 24 格的 Vision 结果与文案按准则加权聚合，得到类型分与调性分（1–10）及置信度。
准则从 profile 目录加载（可配置博主类型与调性）。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from config import GRID_CELLS


def load_criteria(criteria_dir: Union[str, Path]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    d = Path(criteria_dir)
    with open(d / "criteria_type.json", encoding="utf-8") as f:
        ct = json.load(f)
    with open(d / "criteria_tone.json", encoding="utf-8") as f:
        co = json.load(f)
    return ct, co


def _text_match_keywords(text: str, keywords: List[str]) -> int:
    if not text or not keywords:
        return 0
    return sum(1 for kw in keywords if kw in text)


def _cell_type_score(vision_cell: Dict[str, Any], text_raw: str, is_zhiding: bool, criteria_type: Dict[str, Any]) -> Tuple[float, float]:
    weight = criteria_type.get("weight_zhiding", 1.5) if is_zhiding else 1.0
    positive_kw = criteria_type.get("positive_keywords") or []
    negative_kw = criteria_type.get("negative_keywords") or []
    pos_kw_count = _text_match_keywords(text_raw, positive_kw)
    neg_kw_count = _text_match_keywords(text_raw, negative_kw)
    has_baby = vision_cell.get("has_baby_or_child") is True
    has_baby_conf = float(vision_cell.get("has_baby_confidence") or 0)
    person_score = float(vision_cell.get("person_mom_like_score") or 5)
    person_conf = float(vision_cell.get("person_mom_confidence") or 0.5)
    has_maternal = vision_cell.get("has_maternal_products") is True
    maternal_conf = float(vision_cell.get("maternal_confidence") or 0)
    raw = 0.0
    conf_sum = 0.0
    n = 0
    if has_baby:
        raw += 3.0 * has_baby_conf
        conf_sum += has_baby_conf
        n += 1
    raw += (person_score / 10.0) * 4.0 * person_conf
    conf_sum += person_conf
    n += 1
    if has_maternal:
        raw += 2.0 * maternal_conf
        conf_sum += maternal_conf
        n += 1
    raw += min(pos_kw_count * 0.5, 2.0) - min(neg_kw_count * 0.5, 1.5)
    if pos_kw_count or neg_kw_count:
        n += 1
        conf_sum += 0.6
    confidence = conf_sum / n if n else 0.5
    raw = max(0, min(10, raw))
    return (raw * weight, min(1.0, confidence))


def _cell_tone_score(vision_cell: Dict[str, Any], text_raw: str, is_zhiding: bool, criteria_tone: Dict[str, Any]) -> Tuple[float, float]:
    weight = criteria_tone.get("weight_zhiding", 1.5) if is_zhiding else 1.0
    positive_kw = criteria_tone.get("positive_keywords") or []
    tone_score = float(vision_cell.get("tone_refined_score") or 5)
    tone_conf = float(vision_cell.get("tone_refined_confidence") or 0.5)
    kw_count = _text_match_keywords(text_raw, positive_kw)
    raw = (tone_score / 10.0) * 6.0 * tone_conf + min(kw_count * 0.4, 2.0)
    raw = max(0, min(10, raw))
    confidence = min(1.0, tone_conf + 0.2 * min(kw_count, 3))
    return (raw * weight, confidence)


def aggregate_scores(
    cells: List[Dict[str, Any]],
    vision_results: List[Dict[str, Any]],
    criteria_type: Dict[str, Any],
    criteria_tone: Dict[str, Any],
    creator_name: Optional[str] = None,
    creator_desc: Optional[str] = None,
    ref_store_path: Optional[Union[str, Path]] = None,
    cell_embeddings: Optional[List[Optional[List[float]]]] = None,
    similarity_bonus_scale: float = 0.5,
) -> Dict[str, Any]:
    ref_store: List[dict] = []
    max_sim_fn = None
    if ref_store_path and Path(ref_store_path).exists():
        try:
            from embedding_store import load_reference_store, max_similarity_to_references
            ref_store = load_reference_store(ref_store_path)
            max_sim_fn = max_similarity_to_references
        except Exception:
            ref_store = []
    n = min(len(cells), len(vision_results), GRID_CELLS)
    type_scores, type_confs, tone_scores, tone_confs, reasons = [], [], [], [], []
    for i in range(n):
        c = cells[i]
        v = vision_results[i]
        text_raw = (c.get("raw_text") or c.get("title") or "").strip()
        is_zhiding = c.get("has_zhiding", False)
        if v.get("error"):
            type_scores.append(0)
            type_confs.append(0)
            tone_scores.append(0)
            tone_confs.append(0)
            reasons.append("vision_error")
            continue
        ts, tc = _cell_type_score(v, text_raw, is_zhiding, criteria_type)
        os_, oc = _cell_tone_score(v, text_raw, is_zhiding, criteria_tone)
        if ref_store and cell_embeddings and i < len(cell_embeddings) and max_sim_fn is not None:
            try:
                emb = cell_embeddings[i]
                sim_type = max_sim_fn(emb, ref_store, "type")
                sim_tone = max_sim_fn(emb, ref_store, "tone")
                ts += sim_type * similarity_bonus_scale
                os_ += sim_tone * similarity_bonus_scale
            except Exception:
                pass
        type_scores.append(ts)
        type_confs.append(tc)
        tone_scores.append(os_)
        tone_confs.append(oc)
        reasons.append(v.get("brief_reason") or "")
    name_desc = f"{creator_name or ''} {creator_desc or ''}"
    pos_type_kw = criteria_type.get("positive_keywords") or []
    pos_tone_kw = criteria_tone.get("positive_keywords") or []
    name_type_bonus = min(_text_match_keywords(name_desc, pos_type_kw) * 0.5, 1.5)
    name_tone_bonus = min(_text_match_keywords(name_desc, pos_tone_kw) * 0.3, 1.0)
    avg_type = (sum(type_scores) / n if n else 0) + name_type_bonus
    avg_tone = (sum(tone_scores) / n if n else 0) + name_tone_bonus
    avg_type_conf = sum(type_confs) / n if n else 0.5
    avg_tone_conf = sum(tone_confs) / n if n else 0.5
    score_type = max(1, min(10, round(avg_type * 1.0, 1)))
    score_tone = max(1, min(10, round(avg_tone * 1.0, 1)))
    return {
        "score_type": score_type,
        "score_tone": score_tone,
        "confidence_type": round(avg_type_conf, 2),
        "confidence_tone": round(avg_tone_conf, 2),
        "qualifies_type": score_type > 6,
        "qualifies_tone": score_tone > 6,
        "very_qualifies_type": score_type >= 8,
        "very_qualifies_tone": score_tone >= 8,
        "creator_name": creator_name,
        "creator_desc": creator_desc,
        "per_cell_reasons": reasons,
        "raw_type_avg": avg_type,
        "raw_tone_avg": avg_tone,
    }


def run_aggregate_from_dir(
    sliced_dir: Union[str, Path],
    criteria_dir: Union[str, Path],
    creator_name: Optional[str] = None,
    creator_desc: Optional[str] = None,
) -> Dict[str, Any]:
    base = Path(sliced_dir)
    cells = json.loads((base / "cells.json").read_text(encoding="utf-8"))
    vision = json.loads((base / "vision_results.json").read_text(encoding="utf-8"))
    ct, co = load_criteria(criteria_dir)
    return aggregate_scores(cells, vision, ct, co, creator_name=creator_name, creator_desc=creator_desc)
