"""Address parser for Japanese addresses."""
from __future__ import annotations
import re
import json
import os
import logging

from ja_entityparser.parsers.address_normalize import normalize_block

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

# Block number pattern — captures numeric+structural portion.
# Ordered from most-specific to least-specific.
# Fullwidth digits (０-９) are also matched.
# Block number pattern (half/full-width digits, structural kanji, hyphens)
# Alternatives ordered most-specific first.
_BLOCK_PATTERN = re.compile(
    r"([0-9０-９]+丁目[0-9０-９]+番[0-9０-９]*号?"
    r"|[0-9０-９]+番地の[0-9０-９]+"
    r"|[0-9０-９]+番地"
    r"|[0-9０-９]+番[0-9０-９]*号?"
    r"|[0-9０-９]+[-－‐ー][0-9０-９]+(?:[-－‐ー][0-9０-９]+)*"
    r"|[0-9０-９]+の[0-9０-９]+"
    r")"
)

# Fallback: bare trailing number after town name (e.g. 末広町１８４)
_TRAILING_NUMBER_PATTERN = re.compile(
    r"(?<=[^\d０-９])([0-9０-９]+)$"
)


def parse_address_text(text: str) -> dict:
    """Parse a Japanese address string into components.

    Returns a dict with any of: state, city, suburb, house_number, house_number_raw.
    - ``house_number`` is the normalized canonical form (halfwidth digits + hyphens).
    - ``house_number_raw`` preserves the original extracted string for auditing.
    Missing components are omitted from the dict.

    Field names follow libpostal label conventions for cross-language compatibility.
    """
    result = {}
    remaining = text

    # 1. Match prefecture
    for pref in _PREFECTURES_SORTED:
        if remaining.startswith(pref):
            result["state"] = pref
            remaining = remaining[len(pref):]
            break

    # 2. Match municipality (city/ward) — only within known prefecture
    pref_key = result.get("state", "")
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
            result["suburb"] = town_text
        raw_block = block_match.group(0)
        result["house_number"] = normalize_block(raw_block)
        result["house_number_raw"] = raw_block
    else:
        # Fallback: trailing bare number (e.g. 末広町１８４)
        stripped = remaining.strip()
        if stripped:
            trail_match = _TRAILING_NUMBER_PATTERN.search(stripped)
            if trail_match:
                town_text = stripped[:trail_match.start()].strip()
                if town_text:
                    result["suburb"] = town_text
                raw_num = trail_match.group(1)
                result["house_number"] = normalize_block(raw_num)
                result["house_number_raw"] = raw_num
            else:
                result["suburb"] = stripped

    return result
