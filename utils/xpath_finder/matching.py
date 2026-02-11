"""Text normalization and fuzzy matching utilities."""

import re
from difflib import SequenceMatcher


def normalize(text: str) -> str:
    """
    Normalize text for fuzzy comparison:
    - Lowercase
    - Remove quotes/apostrophes
    - Collapse whitespace
    - Remove common punctuation
    """
    if not text:
        return ""
    normalized = text.lower()
    # Remove quotes and apostrophes (including smart quotes)
    normalized = re.sub(r"['\"`\u2018\u2019\u201c\u201d]", "", normalized)
    # Remove other punctuation but keep spaces
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    # Collapse whitespace
    return re.sub(r"\s+", " ", normalized).strip()


def normalize_id(text: str) -> str:
    """
    Normalize for ID/class matching:
    - Remove all separators (-, _, spaces)
    - Lowercase
    """
    if not text:
        return ""
    return re.sub(r"[\s\-_'\"`\u2018\u2019\u201c\u201d]", "", text.lower())


def similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two normalized strings (0.0 to 1.0)."""
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, normalize(text1), normalize(text2)).ratio()


def id_similarity(text1: str, text2: str) -> float:
    """Calculate similarity for ID/class matching."""
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, normalize_id(text1), normalize_id(text2)).ratio()
