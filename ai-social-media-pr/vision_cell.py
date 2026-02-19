"""
对 24 个封面格依次调用 Vision API，得到每格的结构化判断结果。
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from config import GRID_CELLS
from vision_prompt import describe_cover_with_vision


def run_vision_on_cells(
    cover_paths: List[Union[str, Path]],
    api_client: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    results = []
    for path in cover_paths:
        r = describe_cover_with_vision(path, api_client=api_client, model=model, api_key=api_key)
        r["cover_path"] = str(path)
        results.append(r)
    return results


def run_vision_on_sliced_dir(
    sliced_dir: Union[str, Path],
    api_client: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    sliced_dir = Path(sliced_dir)
    covers_dir = sliced_dir / "covers"
    if not covers_dir.exists():
        raise FileNotFoundError(f"covers dir not found: {covers_dir}")
    paths = [covers_dir / f"cell_{i:02d}.jpg" for i in range(GRID_CELLS)]
    return run_vision_on_cells(paths, api_client=api_client, model=model, api_key=api_key)
