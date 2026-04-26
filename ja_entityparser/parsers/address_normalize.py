"""Block-level normalization for Japanese addresses.

Canonical form: halfwidth digits separated by hyphens.
  e.g.  ３－１－５     → 3-1-5
        ３丁目１番５号  → 3-1-5
        ３番地の１      → 3-1
        ６２８番地の１  → 628-1
        １２番地        → 12
        3-1-5           → 3-1-5  (already canonical, no-op)
"""
from __future__ import annotations
import re

# Fullwidth digits → halfwidth
_FW_DIGIT_TRANS = str.maketrans("０１２３４５６７８９", "0123456789")

# Hyphen-like characters → ASCII hyphen
_HYPHENS = re.compile(r"[－‐ー−–—‒]")

# Structural kanji tokens, in order (longest / most-specific first)
_KANJI_SUBS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"丁目"),   "-"),   # 3丁目 → 3-
    (re.compile(r"番地の"), "-"),   # 628番地の1 → 628-1
    (re.compile(r"番地"),   ""),    # 12番地 → 12 (terminal)
    (re.compile(r"番"),     "-"),   # 5番3号 → 5-3
    (re.compile(r"号"),     ""),    # trailing 号 → drop
    (re.compile(r"の"),     "-"),   # catch-all: 3の1 → 3-1
]

# Final validation: canonical form is digits-and-hyphens only, no leading/trailing hyphen
_CANONICAL_RE = re.compile(r"^\d+(-\d+)*$")


def normalize_block(raw: str) -> str:
    """Normalize a raw block/number string to canonical form.

    Returns the normalized string, or the original if normalization
    would produce a clearly wrong result (safety fallback).
    """
    if not raw:
        return raw

    s = raw

    # Step 1: fullwidth digits → halfwidth
    s = s.translate(_FW_DIGIT_TRANS)

    # Step 2: normalize hyphens
    s = _HYPHENS.sub("-", s)

    # Step 3: replace structural kanji tokens
    for pattern, replacement in _KANJI_SUBS:
        s = pattern.sub(replacement, s)

    # Step 4: collapse multiple hyphens; strip leading/trailing hyphens
    s = re.sub(r"-+", "-", s).strip("-")

    # Step 5: validate — must be digits-and-hyphens only
    if s and not _CANONICAL_RE.match(s):
        # Safety fallback: at least apply digit + hyphen normalization
        # but don't corrupt opaque strings
        fallback = raw.translate(_FW_DIGIT_TRANS)
        fallback = _HYPHENS.sub("-", fallback)
        return fallback

    return s
