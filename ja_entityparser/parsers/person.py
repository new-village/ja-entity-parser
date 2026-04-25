"""Person name parser for Japanese names."""
from __future__ import annotations
from typing import List, Optional
import json
import os
import logging

logger = logging.getLogger(__name__)

_NAME_DICT_PATH = os.path.join(os.path.dirname(__file__), "..", "dict", "name_dict.json")

def _load_surnames() -> set:
    try:
        with open(_NAME_DICT_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("surnames", []))
    except Exception:
        return set()

_SURNAMES: set = _load_surnames()

# SudachiPy POS tags for person names
_POS_FAMILY = "人名-姓"
_POS_GIVEN = "人名-名"


def _pos_str(morpheme) -> str:
    """Return the part-of-speech string from a Sudachi morpheme."""
    pos = morpheme.part_of_speech()
    if isinstance(pos, (list, tuple)):
        return "-".join(str(p) for p in pos)
    return str(pos)


def _split_by_sudachi(tokens: List) -> Optional[dict]:
    """Try to split family/given name using SudachiPy POS tags."""
    family_parts = []
    given_parts = []
    family_kana = []
    given_kana = []

    for m in tokens:
        surface = m.surface().strip()
        if not surface:
            continue  # Skip whitespace tokens
        pos = _pos_str(m)
        if _POS_FAMILY in pos:
            family_parts.append(surface)
            family_kana.append(m.reading_form())
        elif _POS_GIVEN in pos:
            given_parts.append(surface)
            given_kana.append(m.reading_form())
        else:
            # Unknown: append to whichever is shorter (heuristic)
            if not given_parts and family_parts:
                given_parts.append(surface)
                given_kana.append(m.reading_form())
            else:
                family_parts.append(surface)
                family_kana.append(m.reading_form())

    if family_parts or given_parts:
        result = {}
        if family_parts:
            result["family_name"] = "".join(family_parts)
            result["family_name_kana"] = "".join(family_kana)
        if given_parts:
            result["given_name"] = "".join(given_parts)
            result["given_name_kana"] = "".join(given_kana)
        return result
    return None


def _split_by_space(text: str) -> Optional[dict]:
    """Split on whitespace: first token = family name, rest = given name."""
    parts = text.split()
    if len(parts) >= 2:
        return {
            "family_name": parts[0].strip(),
            "family_name_kana": "",
            "given_name": "".join(parts[1:]).strip(),
            "given_name_kana": "",
        }
    return None


def _split_by_dict(text: str) -> Optional[dict]:
    """Match leading token against surname dictionary."""
    for surname in sorted(_SURNAMES, key=len, reverse=True):
        if text.startswith(surname) and len(text) > len(surname):
            given = text[len(surname):]
            return {
                "family_name": surname,
                "family_name_kana": "",
                "given_name": given,
                "given_name_kana": "",
            }
    return None


def parse_person_tokens(text: str, tokens: List) -> dict:
    """Parse a person name from text and its Sudachi tokens.

    Strategy:
    1. SudachiPy POS tags (固有名詞-人名-姓/名)
    2. Whitespace split
    3. Surname dictionary lookup
    """
    result = _split_by_sudachi(tokens)
    if not result:
        result = _split_by_space(text)
    if not result:
        result = _split_by_dict(text)
    return result or {}
