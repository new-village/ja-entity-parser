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

# Debug: confirm user dictionary file presence
try:
    user_dic_path = CONFIG_PATH.parent / "ja-entity-parser.dic"
    if user_dic_path.exists():
        logger.debug(f"Sudachi user dictionary: {user_dic_path} ({user_dic_path.stat().st_size} bytes)")
    else:
        logger.warning(f"Sudachi user dictionary NOT FOUND: {user_dic_path}")
except Exception as e:
    logger.debug(f"User dictionary check failed: {e}")


def sudachi_tokenize(text: str) -> List:
    """Tokenize with Sudachi and return a list of Sudachi Morpheme objects.

    When Sudachi returns no tokens (extremely rare), returns a single-element
    list containing the original text to preserve a non-empty result.
    """
    tokens = tk.tokenize(text, mode)
    if not tokens:
        return [text]
    return list(tokens)
