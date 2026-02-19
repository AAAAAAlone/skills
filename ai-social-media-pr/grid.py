"""
从整屏截图中按 4×6 网格切分出 24 个格子，每格拆成封面图与文案区。
截图默认含顶部登录栏与左侧导航栏，由 config 的 CROP_* 排除。
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Union

from PIL import Image

from config import (
    CROP_BOTTOM,
    CROP_LEFT,
    CROP_RIGHT,
    CROP_TOP,
    CELL_COVER_HEIGHT_RATIO,
    GRID_COLS,
    GRID_ROWS,
)


def open_image(source: Union[str, Path, Image.Image]) -> Image.Image:
    """统一打开为 RGB 图."""
    if isinstance(source, Image.Image):
        return source.convert("RGB") if source.mode != "RGB" else source
    im = Image.open(source).convert("RGB")
    return im


def crop_content_region(img: Image.Image) -> Image.Image:
    """按配置比例裁掉顶部栏与左侧栏，只保留 4×6 内容区."""
    w, h = img.size
    x0 = int(w * CROP_LEFT)
    x1 = int(w * CROP_RIGHT)
    y0 = int(h * CROP_TOP)
    y1 = int(h * CROP_BOTTOM)
    return img.crop((x0, y0, x1, y1))


def slice_grid(
    img: Image.Image,
    rows: int = GRID_ROWS,
    cols: int = GRID_COLS,
    cover_height_ratio: float = CELL_COVER_HEIGHT_RATIO,
) -> List[Tuple[Image.Image, Image.Image]]:
    """
    将已裁好内容区的图按 rows×cols 切格，每格再拆成封面图 + 文案区。
    返回 list of (cover_pil, text_region_pil)，长度 rows*cols。
    """
    im = crop_content_region(img)
    w, h = im.size
    cell_w = w / cols
    cell_h = h / rows
    cover_h_per_cell = cell_h * cover_height_ratio
    for row in range(rows):
        for col in range(cols):
            x0 = int(col * cell_w)
            x1 = int((col + 1) * cell_w)
            y_cell_top = int(row * cell_h)
            y_cover_bottom = int(y_cell_top + cover_h_per_cell)
            y_cell_bottom = int((row + 1) * cell_h)
            cover = im.crop((x0, y_cell_top, x1, y_cover_bottom))
            text_region = im.crop((x0, y_cover_bottom, x1, y_cell_bottom))
            yield (cover, text_region)


def slice_screenshot(
    source: Union[str, Path, Image.Image],
    rows: int = GRID_ROWS,
    cols: int = GRID_COLS,
    cover_height_ratio: float = CELL_COVER_HEIGHT_RATIO,
) -> List[Tuple[Image.Image, Image.Image]]:
    """
    从整屏截图切出 24 个 (封面图, 文案区图)。
    source: 截图路径或 PIL Image。
    """
    img = open_image(source)
    return list(slice_grid(img, rows=rows, cols=cols, cover_height_ratio=cover_height_ratio))
