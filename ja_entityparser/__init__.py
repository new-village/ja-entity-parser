import logging
from .parser import parse
from .normalizer import normalize

# Ensure library logs defer to the caller's configuration (no output by default)
logging.getLogger(__name__).addHandler(logging.NullHandler())

def corporate_parser(text: str) -> dict:
    """
    入力文字列を normalize し、parse して結果を返す。
    戻り値は {'input': str, 'legal_form': ..., 'brand_name': ...}
    """
    result = {'input': text}
    normalized = normalize(text)
    result.update(parse(normalized))
    return result

__all__ = ["corporate_parser"]
