from __future__ import annotations
from typing import List
import logging

logger = logging.getLogger(__name__)


def _extract_brand_name(tokens: List) -> str:
    """Extract brand name from Sudachi tokens."""
    return ''.join([m.surface() for m in tokens])


def _extract_brand_kana(tokens: List) -> str:
    """Extract kana reading form of the brand name from Sudachi tokens."""
    return ''.join([m.reading_form() for m in tokens if 'キゴウ' not in m.reading_form()])


def extract_business(tokens: List) -> dict:
    """Extract corporate name components from Sudachi tokens."""
    parsed = {'input': ''.join([m.surface() for m in tokens])}

    for m in tokens:
        if "法人種別" in m.part_of_speech():
            parsed['legal_form'] = m.normalized_form()
            tokens.remove(m)

    parsed['brand_name'] = _extract_brand_name(tokens)
    parsed['brand_kana'] = _extract_brand_kana(tokens)
    logger.debug([{'surface': m.surface(), 'pos': m.part_of_speech()} for m in tokens])
    parsed.pop('input', None)
    return parsed


def parse_corporate_tokens(tokens: List) -> dict:
    """Parse corporate name from already-tokenized Sudachi tokens."""
    return extract_business(tokens)
