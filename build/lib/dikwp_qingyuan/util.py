from __future__ import annotations
import hashlib, json, re
from typing import Iterable, Any

def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(v)))

def norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())

def hits(text: str, patterns: Iterable[str]) -> list[str]:
    t = norm(text)
    return [p for p in patterns if p.lower() in t]

def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def content_id(value: Any) -> str:
    return sha256_text(canonical_json(value))[:20]
