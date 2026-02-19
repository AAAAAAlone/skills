"""
流水线：整屏截图 -> 4×6 切格 -> 每格 OCR 文案区（或使用已提供的笔记标题）-> 输出 24 个 (封面图, 文案结构化)。
达人名称、简介、每个笔记标题可由外部脚本提供，此处通过 note_titles 传入即视为“已有”。
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple, Union

from PIL import Image

from grid import slice_screenshot
from ocr_utils import extract_cell_text


def run_slice_and_ocr(
    screenshot_path: Union[str, Path],
    ocr_lang: str = "chi_sim+eng",
    note_titles: Optional[List[str]] = None,
) -> List[Tuple[Image.Image, dict]]:
    """
    对一张整屏截图：切 24 格，每格 OCR 文案区；若提供 note_titles（长度 24），则用其覆盖每格 title。
    返回 list of (cover_pil, cell_info)，共 24 项。
    """
    cells = slice_screenshot(screenshot_path)
    out: List[Tuple[Image.Image, dict]] = []
    for idx, (cover_im, text_region_im) in enumerate(cells):
        cell_info = extract_cell_text(text_region_im, lang=ocr_lang)
        if note_titles and idx < len(note_titles) and note_titles[idx]:
            cell_info["title"] = note_titles[idx]
        out.append((cover_im, cell_info))
    return out


def run_slice_and_ocr_to_dir(
    screenshot_path: Union[str, Path],
    output_dir: Union[str, Path],
    ocr_lang: str = "chi_sim+eng",
    save_covers: bool = True,
    save_text_regions: bool = False,
    note_titles: Optional[List[str]] = None,
) -> List[dict]:
    """
    切格 + OCR，封面写入 output_dir/covers/。若提供 note_titles（24 项），则每格 title 以之为准。
    返回 24 个 cell 的摘要（含 cover 路径、title、raw_text、has_zhiding、likes_approx）。
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    covers_dir = output_dir / "covers"
    if save_covers:
        covers_dir.mkdir(parents=True, exist_ok=True)
    text_regions_dir = output_dir / "text_regions" if save_text_regions else None
    if text_regions_dir:
        text_regions_dir.mkdir(parents=True, exist_ok=True)

    cells = slice_screenshot(screenshot_path)
    results: List[dict] = []
    for idx, (cover_im, text_region_im) in enumerate(cells):
        cell_info = extract_cell_text(text_region_im, lang=ocr_lang)
        if note_titles and idx < len(note_titles) and note_titles[idx]:
            cell_info["title"] = note_titles[idx]
        cover_path: Optional[str] = None
        if save_covers:
            cover_path = str(covers_dir / f"cell_{idx:02d}.jpg")
            cover_im.save(cover_path, "JPEG", quality=85)
        if text_regions_dir:
            text_region_im.save(text_regions_dir / f"cell_{idx:02d}.jpg", "JPEG", quality=85)
        results.append({
            "index": idx,
            "cover_path": cover_path,
            "raw_text": cell_info["raw"],
            "title": cell_info["title"],
            "has_zhiding": cell_info["has_zhiding"],
            "likes_approx": cell_info["likes_approx"],
        })
    return results
