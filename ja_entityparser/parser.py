"""Backward-compatible parser module. Use parsers/corporate.py for new code."""
from __future__ import annotations
from typing import List
from .tokenizer import sudachi_tokenize as _sudachi_tokenize_impl
from .parsers.corporate import extract_business
import logging

logger = logging.getLogger(__name__)


def _sudachi_tokenize(text: str) -> List:
    """Tokenize with Sudachi. Kept for backward compatibility / monkeypatching in tests."""
    return _sudachi_tokenize_impl(text)


def parse(text: str) -> dict:
    """Normalize input and tokenize it with Sudachi, then extract business components."""
    token = _sudachi_tokenize(text)
    return extract_business(token)
