"""
对单张文案区图像做 OCR，提取标题、话题、点赞数等文本。
当外部已提供笔记标题时，以传入的 title 为准，OCR 仅作补充。
"""
from __future__ import annotations

from typing import Optional

from PIL import Image

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


def ocr_text_region(
    image: Image.Image,
    lang: str = "chi_sim+eng",
) -> str:
    """
    对文案区图像做 OCR，返回整段文本。
    若未安装 pytesseract 或 Tesseract，返回空字符串。
    """
    if not PYTESSERACT_AVAILABLE:
        return ""
    try:
        img = image.convert("L")
        text = pytesseract.image_to_string(img, lang=lang)
        return (text or "").strip()
    except Exception:
        return ""


def extract_cell_text(
    text_region_image: Image.Image,
    lang: str = "chi_sim+eng",
) -> dict:
    """
    从单格文案区 OCR 结果中提取结构化字段。
    返回 {"raw": str, "title": str, "has_zhiding": bool, "likes_approx": Optional[int]}
    """
    raw = ocr_text_region(text_region_image, lang=lang)
    has_zhiding = "置顶" in raw
    title = raw
    likes_approx: Optional[int] = None
    words = raw.replace("\n", " ").split()
    for w in reversed(words):
        w_clean = "".join(c for c in w if c.isdigit())
        if w_clean and len(w_clean) <= 10:
            try:
                likes_approx = int(w_clean)
                break
            except ValueError:
                pass
    return {
        "raw": raw,
        "title": title,
        "has_zhiding": has_zhiding,
        "likes_approx": likes_approx,
    }
