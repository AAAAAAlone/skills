"""
基于 scoring.json 规则与 24 格 Vision 结果做规则打分（1-10），并应用两项细化：
1. 婴幼儿年龄：仅 0-3 岁小宝宝计为婴幼儿元素，大孩子不计入且扣分
2. 调性不符：封面杂乱/广告感强时降调性，不视为真实宝妈
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from config import GRID_CELLS


def load_scoring(profile_dir: Union[str, Path]) -> Dict[str, Any]:
    p = Path(profile_dir)
    path = p / "scoring.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _get(v: Dict[str, Any], key: str, default: Any = None):
    if v.get("error"):
        return default
    return v.get(key, default)


def _is_infant_cell(v: Dict[str, Any]) -> bool:
    """是否算作「婴幼儿元素」：有宝宝且判定为 0-3 岁，且非杂乱广告感。"""
    has_baby = _get(v, "has_baby_or_child") is True
    age_0_3 = _get(v, "child_age_0_3") is True
    clutter = _get(v, "cover_cluttered_or_ad_like") is True
    if not has_baby:
        return False
    if clutter:
        return False
    return age_0_3 if age_0_3 is not None else has_baby


def _is_real_baby_cell(v: Dict[str, Any]) -> bool:
    """是否「真实带娃」：婴幼儿元素 + 真实居家场景感，非 AI 军装。"""
    if not _is_infant_cell(v):
        return False
    ai_style = _get(v, "ai_army_or_filter") is True
    if ai_style:
        return False
    real_home = _get(v, "real_home_life_scene") is True
    return real_home if real_home is not None else True


def aggregate_by_scoring(
    cells: List[Dict[str, Any]],
    vision_results: List[Dict[str, Any]],
    scoring: Dict[str, Any],
    creator_name: Optional[str] = None,
    creator_desc: Optional[str] = None,
) -> Dict[str, Any]:
    """
    按 scoring.json 规则汇总得分，并应用婴幼儿年龄、杂乱调性两项细化。
    返回 score_total (1-10), perfect_match (>= threshold), rule_breakdown。
    """
    if not scoring:
        return {"error": "no scoring config", "score_total": 0, "perfect_match": False}
    sys_cfg = scoring.get("scoring_system") or {}
    total_scale = sys_cfg.get("total_scale", 10)
    qualifies_threshold = sys_cfg.get("qualifies_threshold", 6)
    very_recommended_threshold = sys_cfg.get("very_recommended_threshold", 9)
    rules = sys_cfg.get("rules") or []
    grid_scope = min(scoring.get("grid_scope", 24), GRID_CELLS)
    n = min(len(cells), len(vision_results), grid_scope)

    # 置顶格：取 has_zhiding 的格子，按索引顺序前 3 个
    pinned_indices = [i for i in range(n) if (cells[i].get("has_zhiding") is True)][:3]
    # 真实带娃：前三位置顶中至少 2 个为真实带娃
    real_baby_in_pinned = sum(1 for i in pinned_indices if _is_real_baby_cell(vision_results[i])) if pinned_indices else 0
    rule_pinned = 3.0 if (len(pinned_indices) >= 2 and real_baby_in_pinned >= 2) else (1.5 if real_baby_in_pinned >= 1 else 0)

    # 24 格中超过 5 个婴幼儿元素（仅 0-3 岁 + 非杂乱）
    infant_count = sum(1 for i in range(n) if _is_infant_cell(vision_results[i]))
    rule_infant = 2.5 if infant_count >= 5 else (1.25 if infant_count >= 3 else 0)

    # 封面包含奶粉、纸尿裤、教辅等实物
    maternal_count = sum(1 for i in range(n) if _get(vision_results[i], "has_maternal_products") is True)
    rule_maternal = 2.0 if maternal_count >= 1 else 0

    # 背景为真实居家/生活化场景（多数格）
    real_home_count = sum(1 for i in range(n) if _get(vision_results[i], "real_home_life_scene") is True)
    rule_home = 1.5 if real_home_count >= 5 else (0.75 if real_home_count >= 2 else 0)

    # 未使用 AI 军装/AI 创作（多数格无）
    ai_count = sum(1 for i in range(n) if _get(vision_results[i], "ai_army_or_filter") is True)
    rule_no_ai = 1.0 if ai_count <= 2 else 0

    # 名字/简介包含 妈/麻/育儿/记录成长
    name_desc = f"{creator_name or ''} {creator_desc or ''}"
    bio_kw = ["妈", "麻", "育儿", "记录成长"]
    bio_match = any(kw in name_desc for kw in bio_kw)
    rule_bio = 2.0 if bio_match else 0

    raw_total = rule_pinned + rule_infant + rule_maternal + rule_home + rule_no_ai + rule_bio
    # 归一化到 total_scale（规则总分约 12，缩放到 10）
    max_possible = 3.0 + 2.5 + 2.0 + 1.5 + 1.0 + 2.0
    score_total = max(1, min(total_scale, round(raw_total * (total_scale / max_possible), 1)))

    # 调性细化：若杂乱/广告感格子占比过高，扣分
    clutter_count = sum(1 for i in range(n) if _get(vision_results[i], "cover_cluttered_or_ad_like") is True)
    if clutter_count >= n // 2 and score_total > 5:
        score_total = max(1, round(score_total - 1.5, 1))

    return {
        "score_total": score_total,
        "qualifies": score_total > qualifies_threshold,
        "very_recommended": score_total > very_recommended_threshold,
        "qualifies_threshold": qualifies_threshold,
        "very_recommended_threshold": very_recommended_threshold,
        "rule_breakdown": {
            "pinned_top3_real_baby": rule_pinned,
            "grid_infant_count_5": rule_infant,
            "maternal_products": rule_maternal,
            "real_home_scene": rule_home,
            "no_ai_army": rule_no_ai,
            "bio_keywords": rule_bio,
        },
        "raw_total": round(raw_total, 2),
        "refinements": {
            "infant_cells_count": infant_count,
            "clutter_cells_count": clutter_count,
        },
        "creator_name": creator_name,
        "creator_desc": creator_desc,
    }


def run_scoring_from_dir(
    sliced_dir: Union[str, Path],
    profile_dir: Union[str, Path],
    creator_name: Optional[str] = None,
    creator_desc: Optional[str] = None,
) -> Dict[str, Any]:
    base = Path(sliced_dir)
    profile = Path(profile_dir)
    cells = json.loads((base / "cells.json").read_text(encoding="utf-8"))
    vision = json.loads((base / "vision_results.json").read_text(encoding="utf-8"))
    scoring = load_scoring(profile)
    return aggregate_by_scoring(cells, vision, scoring, creator_name=creator_name, creator_desc=creator_desc)
