"""
封面向量化：对样本正例封面生成 embedding 并存储；对新封面算 embedding 与参考向量相似度，可融入打分。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Union

try:
    from sentence_transformers import SentenceTransformer
    _ST_AVAILABLE = True
except ImportError:
    _ST_AVAILABLE = False


def get_image_embedding_model():
    if not _ST_AVAILABLE:
        return None
    try:
        return SentenceTransformer("clip-ViT-B-32")
    except Exception:
        return None


def embed_image(image_path: Union[str, Path], model) -> Optional[List[float]]:
    if model is None:
        return None
    try:
        path = Path(image_path)
        if not path.exists():
            return None
        emb = model.encode(str(path))
        return emb.tolist()
    except Exception:
        return None


def embed_images(image_paths: List[Union[str, Path]], model) -> List[Optional[List[float]]]:
    if model is None:
        return [None] * len(image_paths)
    try:
        paths = [str(Path(p)) for p in image_paths]
        embs = model.encode(paths)
        return [e.tolist() for e in embs]
    except Exception:
        return [None] * len(image_paths)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def build_reference_store(cover_paths: List[Union[str, Path]], labels: List[dict], output_path: Union[str, Path]) -> bool:
    model = get_image_embedding_model()
    if model is None:
        return False
    embs = embed_images(cover_paths, model)
    store = []
    for i, (path, lab) in enumerate(zip(cover_paths, labels)):
        if embs[i] is None:
            continue
        store.append({"id": f"ref_{i}", "cover_path": str(path), "embedding": embs[i], **lab})
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)
    return True


def load_reference_store(path: Union[str, Path]) -> List[dict]:
    p = Path(path)
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def max_similarity_to_references(query_embedding: Optional[List[float]], reference_store: List[dict], label_filter: Optional[str] = None) -> float:
    if not query_embedding or not reference_store:
        return 0.0
    best = 0.0
    for ref in reference_store:
        emb = ref.get("embedding")
        if not emb:
            continue
        if label_filter == "type" and ref.get("label_type") != "宝妈":
            continue
        if label_filter == "tone" and not ref.get("label_tone"):
            continue
        sim = cosine_similarity(query_embedding, emb)
        w = 1.5 if ref.get("weight") == "high" else 1.0
        best = max(best, sim * w)
    return best
