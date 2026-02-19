#!/usr/bin/env python3
"""
从 samples/nice 目录的截图自动生成参考向量库。
对每张截图：切格 → Vision 识别正例格子（0-3岁婴幼儿、真实居家、非杂乱）→ 生成 embedding → 保存到 profile 目录。
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

from build_ref_store import build_from_sliced_dir
from embedding_store import build_reference_store, get_image_embedding_model
from slice_and_ocr import run_slice_and_ocr_to_dir
from vision_cell import run_vision_on_sliced_dir
from vision_prompt import describe_cover_with_vision


def _is_positive_cell(v: dict) -> bool:
    """判断是否为正例格子：0-3岁婴幼儿 + 真实居家 + 非杂乱 + 非AI军装。"""
    if v.get("error"):
        return False
    has_baby = v.get("has_baby_or_child") is True
    age_0_3 = v.get("child_age_0_3") is True
    clutter = v.get("cover_cluttered_or_ad_like") is True
    ai_style = v.get("ai_army_or_filter") is True
    real_home = v.get("real_home_life_scene") is True
    if not has_baby or not age_0_3:
        return False
    if clutter or ai_style:
        return False
    return real_home if real_home is not None else True


def process_samples_to_ref_store(
    samples_dir: Path,
    profile_dir: Path,
    api_client: str = "openai",
    vision_model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> bool:
    """
    处理 samples_dir 下所有截图，提取正例格子，生成参考向量并保存到 profile_dir/ref_embeddings.json。
    """
    samples_dir = Path(samples_dir)
    profile_dir = Path(profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    screenshot_files = list(samples_dir.glob("*.png")) + list(samples_dir.glob("*.jpg"))
    if not screenshot_files:
        print(f"未找到截图文件: {samples_dir}")
        return False

    print(f"找到 {len(screenshot_files)} 张截图，开始处理...")
    all_positive_covers: List[Path] = []
    all_labels: List[dict] = []

    for idx, screenshot in enumerate(screenshot_files):
        print(f"\n[{idx+1}/{len(screenshot_files)}] 处理: {screenshot.name}")
        temp_dir = PROJECT_ROOT / "temp_sliced" / screenshot.stem
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 切格 + OCR
            run_slice_and_ocr_to_dir(screenshot, temp_dir)
            # Vision 分析
            vision_results = run_vision_on_sliced_dir(
                temp_dir, api_client=api_client, model=vision_model, api_key=api_key
            )
            # 找出正例格子
            positive_indices = [i for i, v in enumerate(vision_results) if _is_positive_cell(v)]
            print(f"  正例格子: {len(positive_indices)}/{len(vision_results)}")
            
            for i in positive_indices:
                cover_path = temp_dir / "covers" / f"cell_{i:02d}.jpg"
                if cover_path.exists():
                    all_positive_covers.append(cover_path)
                    all_labels.append({
                        "label_type": "宝妈",
                        "label_tone": "真实生活感",
                        "weight": "high",
                        "source": screenshot.name,
                        "cell_index": i,
                    })
        except Exception as e:
            print(f"  处理失败: {e}")
            continue

    if not all_positive_covers:
        print("未找到正例格子")
        return False

    print(f"\n共提取 {len(all_positive_covers)} 个正例封面，生成参考向量...")
    output_path = profile_dir / "ref_embeddings.json"
    success = build_reference_store(all_positive_covers, all_labels, output_path)
    
    if success:
        print(f"参考向量已保存: {output_path}")
        print(f"  正例数量: {len(all_positive_covers)}")
        return True
    else:
        print("生成失败（可能未安装 sentence-transformers）")
        return False


def main():
    parser = argparse.ArgumentParser(description="从 samples/nice 生成参考向量")
    parser.add_argument("--samples", type=str, default=None, help="样本目录，默认 samples/nice")
    parser.add_argument("-p", "--profile", type=str, default="douyin_mom_finder", help="profile 名")
    parser.add_argument("--api", type=str, default="openai", choices=["openai", "gemini", "anthropic"])
    parser.add_argument("--model", type=str, default=None)
    args = parser.parse_args()

    samples_dir = Path(args.samples) if args.samples else PROJECT_ROOT / "samples" / "nice"
    profile_dir = PROJECT_ROOT / "profiles" / args.profile
    
    if not samples_dir.exists():
        print(f"样本目录不存在: {samples_dir}")
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    success = process_samples_to_ref_store(
        samples_dir, profile_dir,
        api_client=args.api, vision_model=args.model, api_key=api_key
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
