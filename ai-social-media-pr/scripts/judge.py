#!/usr/bin/env python3
"""
对整屏截图做 4×6 切格、Vision 分析、聚合，输出类型分与调性分。
达人名称、简介、笔记标题由参数传入（视为已由外部脚本提供）。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from aggregate_score import aggregate_scores, load_criteria
from scoring_aggregate import aggregate_by_scoring, load_scoring
from slice_and_ocr import run_slice_and_ocr_to_dir
from vision_cell import run_vision_on_sliced_dir


def run_full_judge(
    screenshot_path: Path,
    output_dir: Path,
    profile_dir: Path,
    creator_name: Optional[str] = None,
    creator_desc: Optional[str] = None,
    note_titles: Optional[List[str]] = None,
    api_client: str = "openai",
    vision_model: Optional[str] = None,
    ref_store_path: Optional[Path] = None,
    similarity_bonus_scale: float = 0.5,
    ocr_lang: str = "chi_sim+eng",
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_slice_and_ocr_to_dir(
        screenshot_path, output_dir,
        ocr_lang=ocr_lang,
        note_titles=note_titles,
    )
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    vision_results = run_vision_on_sliced_dir(output_dir, api_client=api_client, model=vision_model, api_key=api_key)
    with open(output_dir / "vision_results.json", "w", encoding="utf-8") as f:
        json.dump(vision_results, f, ensure_ascii=False, indent=2)

    cell_embeddings = None
    if ref_store_path and ref_store_path.exists():
        try:
            from embedding_store import get_image_embedding_model, embed_images
            model = get_image_embedding_model()
            if model is not None:
                from config import GRID_CELLS
                cover_paths = [output_dir / "covers" / f"cell_{i:02d}.jpg" for i in range(GRID_CELLS)]
                cell_embeddings = embed_images(cover_paths, model)
        except Exception:
            cell_embeddings = None

    cells = json.loads((output_dir / "cells.json").read_text(encoding="utf-8"))
    scoring = load_scoring(profile_dir)
    
    # 默认使用 profile 目录下的 ref_embeddings.json（如果存在且未指定 --ref-store）
    if ref_store_path is None:
        default_ref = profile_dir / "ref_embeddings.json"
        if default_ref.exists():
            ref_store_path = default_ref
    
    if scoring:
        result = aggregate_by_scoring(
            cells, vision_results, scoring,
            creator_name=creator_name, creator_desc=creator_desc,
        )
        result["profile_mode"] = "scoring"
        # scoring 模式也支持向量相似度加分（通过 aggregate_score 的逻辑）
        if ref_store_path and ref_store_path.exists():
            try:
                from embedding_store import get_image_embedding_model, embed_images
                model = get_image_embedding_model()
                if model is not None:
                    from config import GRID_CELLS
                    cover_paths = [output_dir / "covers" / f"cell_{i:02d}.jpg" for i in range(GRID_CELLS)]
                    cell_embeddings = embed_images(cover_paths, model)
                    # 对每个格子的原始分做相似度加权（简单加法）
                    from embedding_store import load_reference_store, max_similarity_to_references
                    ref_store = load_reference_store(ref_store_path)
                    for i in range(min(len(cell_embeddings), len(result.get("rule_breakdown", {})))):
                        if cell_embeddings[i]:
                            sim = max_similarity_to_references(cell_embeddings[i], ref_store, "type")
                            # 相似度高时给总分加分（最多+1分）
                            if sim > 0.7:
                                result["score_total"] = min(10, round(result.get("score_total", 0) + sim * 0.5, 1))
            except Exception:
                pass
    else:
        ct, co = load_criteria(profile_dir)
        result = aggregate_scores(
            cells, vision_results, ct, co,
            creator_name=creator_name, creator_desc=creator_desc,
            ref_store_path=str(ref_store_path) if ref_store_path else None,
            cell_embeddings=cell_embeddings,
            similarity_bonus_scale=similarity_bonus_scale,
        )
        result["profile_mode"] = "criteria"
    with open(output_dir / "result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def main():
    parser = argparse.ArgumentParser(description="截图分析：类型/调性 1–10 分")
    parser.add_argument("screenshot", type=str, help="整屏截图路径")
    parser.add_argument("-o", "--output", type=str, default=None, help="输出目录")
    parser.add_argument("-p", "--profile", type=str, default="douyin_mom_finder", help="profile 名，对应 profiles/<name>/；默认 douyin_mom_finder（规则打分）")
    parser.add_argument("--creator-name", type=str, default=None)
    parser.add_argument("--creator-desc", type=str, default=None)
    parser.add_argument("--note-titles", type=str, default=None, help='JSON 数组，24 个笔记标题，如 \'["t1","t2",...]\'')
    parser.add_argument("--api", type=str, default="openai", choices=["openai", "gemini", "anthropic"])
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--ref-store", type=str, default=None)
    parser.add_argument("--similarity-bonus", type=float, default=0.5)
    args = parser.parse_args()

    base = Path(args.screenshot).resolve().parent
    out = Path(args.output).resolve() if args.output else base / "judge_out"
    profile_dir = PROJECT_ROOT / "profiles" / args.profile
    if not profile_dir.exists():
        print(f"profile 不存在: {profile_dir}")
        sys.exit(1)
    ref_store = Path(args.ref_store).resolve() if args.ref_store else None
    note_titles = None
    if args.note_titles:
        try:
            note_titles = json.loads(args.note_titles)
            if len(note_titles) < 24:
                note_titles = note_titles + [""] * (24 - len(note_titles))
            note_titles = note_titles[:24]
        except Exception:
            note_titles = None

    result = run_full_judge(
        Path(args.screenshot).resolve(),
        out,
        profile_dir,
        creator_name=args.creator_name or None,
        creator_desc=args.creator_desc or None,
        note_titles=note_titles,
        api_client=args.api,
        vision_model=args.model,
        ref_store_path=ref_store,
        similarity_bonus_scale=args.similarity_bonus,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("profile_mode") == "scoring":
        print(f"\n总分: {result.get('score_total', 0)}  合格>6: {result.get('qualifies')}  非常推荐>9: {result.get('very_recommended')}")
    else:
        print(f"\n类型分: {result.get('score_type')}  符合>6: {result.get('qualifies_type')}  非常符合≥8: {result.get('very_qualifies_type')}")
        print(f"调性分: {result.get('score_tone')}  符合>6: {result.get('qualifies_tone')}  非常符合≥8: {result.get('very_qualifies_tone')}")


if __name__ == "__main__":
    main()
