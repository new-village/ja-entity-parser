from __future__ import annotations
from typing import List
from sudachipy import dictionary, tokenizer
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Resolve Sudachi config relative to this file to avoid CWD issues
CONFIG_PATH = (Path(__file__).resolve().parent / "dict" / "sudachi.json")

# Create tokenizer
tk = dictionary.Dictionary(config_path=str(CONFIG_PATH)).create()
mode = tokenizer.Tokenizer.SplitMode.C

# Debug: confirm user dictionary file presence (logging must be enabled by the app)
try:
    user_dic_path = CONFIG_PATH.parent / "ja-entity-parser.dic"
    if user_dic_path.exists():
        logger.debug(f"Sudachi user dictionary: {user_dic_path} ({user_dic_path.stat().st_size} bytes)")
    else:
        logger.warning(f"Sudachi user dictionary NOT FOUND: {user_dic_path}")
except Exception as e:
    logger.debug(f"User dictionary check failed: {e}")

def _sudachi_tokenize(text: str) -> List:
    """Tokenize with Sudachi and return a list of Sudachi Morpheme objects.

    Note: When Sudachi returns no tokens (extremely rare), this returns a
    single-element list containing the original text to preserve a non-empty
    result for downstream consumers.
    """
    tokens = tk.tokenize(text, mode)
    if not tokens:
        return [text]
    
    return list(tokens)

def _extract_brand_name(tokens: List) -> str:
    """Extract brand name from Sudachi tokens."""
    brand_name = ''.join([m.surface() for m in tokens])
    return brand_name

def _extract_brand_kana(tokens: List) -> str:
    """Extract kana reading form of the brand name from Sudachi tokens."""
    brand_kana = ''.join([m.reading_form() for m in tokens if 'キゴウ' not in m.reading_form()])
    return brand_kana

def extract_business(tokens: List) -> dict[str]:
    """Extract business names from Sudachi tokens.

    This function is a placeholder for future logic to extract business names
    from the tokenized input. Currently, it returns the original tokens as strings.
    """
    parsed_strings = {'input': ''.join([m.surface() for m in tokens])}

    for m in tokens:
        # 法人種別の判定: 品詞情報に「法人種別」が含まれる場合
        if "法人種別" in m.part_of_speech():
            parsed_strings['legal_form'] = m.normalized_form()
            tokens.remove(m)

    # 企業名の抽出: 品詞情報に「企業名」が含まれる場合
    parsed_strings['brand_name'] = _extract_brand_name(tokens)
    # 企業名カナの抽出: 品詞情報に「企業名」が含まれる場合
    parsed_strings['brand_kana'] = _extract_brand_kana(tokens)
    logger.debug([{'surface': m.surface(), 'pos': m.part_of_speech()} for m in tokens])
    # 'input' を削除
    parsed_strings.pop('input', None)
    return parsed_strings


def parse(text: str) -> List[str]:
    """Normalize input and tokenize it with Sudachi.

    Returns a list of Sudachi Morpheme objects (or a single string element
    when tokenization yields no tokens).
    """
    token = _sudachi_tokenize(text)
    return extract_business(token)
