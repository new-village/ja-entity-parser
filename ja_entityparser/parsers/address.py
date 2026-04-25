"""Address parser for Japanese addresses."""
from __future__ import annotations
import re
import json
import os
import logging

logger = logging.getLogger(__name__)

_DICT_PATH = os.path.join(os.path.dirname(__file__), "..", "dict", "address_parts.json")


def _load_address_parts():
    try:
        with open(_DICT_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"prefectures": [], "municipalities": {}}


_ADDRESS_PARTS = _load_address_parts()
_PREFECTURES: list = _ADDRESS_PARTS.get("prefectures", [])
# Sort by length descending to match longer names first
_PREFECTURES_SORTED = sorted(_PREFECTURES, key=len, reverse=True)

_MUNICIPALITIES: dict = _ADDRESS_PARTS.get("municipalities", {})
# Build a flat sorted list of (prefecture, municipality) for matching
_ALL_MUNICIPALITIES: list = [
    (pref, muni)
    for pref, munis in _MUNICIPALITIES.items()
    for muni in munis
]

# Block number patterns: 3-1-5 / 3丁目1番5号 / ３－１－５
_BLOCK_PATTERN = re.compile(
    r'(\d+丁目\d+番\d*号?|\d+[-－]\d+(?:[-－]\d+)*|\d+番地\d*)'
)


def parse_address_text(text: str) -> dict:
    """Parse a Japanese address string into components.

    Returns a dict with any of: prefecture, city, town, block.
    Missing components are omitted from the dict.
    """
    result = {}
    remaining = text

    # 1. Match prefecture
    for pref in _PREFECTURES_SORTED:
        if remaining.startswith(pref):
            result["prefecture"] = pref
            remaining = remaining[len(pref):]
            break

    # 2. Match municipality (city/ward) — only within known prefecture
    pref_key = result.get("prefecture", "")
    candidates = _MUNICIPALITIES.get(pref_key, [])
    # If prefecture not found or no candidates, try all municipalities
    if not candidates:
        candidates = [muni for _, muni in _ALL_MUNICIPALITIES]
    candidates_sorted = sorted(candidates, key=len, reverse=True)

    for muni in candidates_sorted:
        if remaining.startswith(muni):
            result["city"] = muni
            remaining = remaining[len(muni):]
            break

    # 3. Find block number
    block_match = _BLOCK_PATTERN.search(remaining)
    if block_match:
        block_start = block_match.start()
        town_text = remaining[:block_start].strip()
        if town_text:
            result["town"] = town_text
        result["block"] = block_match.group(0)
    else:
        # No block found — remaining is all town
        if remaining.strip():
            result["town"] = remaining.strip()

    return result
