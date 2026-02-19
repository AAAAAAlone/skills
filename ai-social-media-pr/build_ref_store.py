"""
从样本截图的封面格生成参考向量并保存。使用 config.GRID_CELLS（24）。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Union

from config import GRID_CELLS
from embedding_store import build_reference_store, get_image_embedding_model


def build_from_sliced_dir(
    sliced_dir: Union[str, Path],
    positive_indices: List[int],
    output_path: Union[str, Path],
    label_type: str = "宝妈",
    label_tone: str = "精致妈妈",
    weight: str = "high",
) -> bool:
    sliced_dir = Path(sliced_dir)
    covers_dir = sliced_dir / "covers"
    if not covers_dir.exists():
        print(f"covers 目录不存在: {covers_dir}")
        return False
    cover_paths = [covers_dir / f"cell_{i:02d}.jpg" for i in positive_indices]
    labels = [{"label_type": label_type, "label_tone": label_tone, "weight": weight}] * len(cover_paths)
    return build_reference_store(cover_paths, labels, output_path)
