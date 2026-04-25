import logging
import warnings
from .normalizer import normalize
from .tokenizer import sudachi_tokenize
from .parsers.corporate import extract_business
from .parsers.person import parse_person_tokens

logging.getLogger(__name__).addHandler(logging.NullHandler())


def parse_corporate(text: str) -> dict:
    """Parse a Japanese corporate name into components.

    Returns a dict with keys: input, legal_form (if found), brand_name,
    brand_kana, normalized.
    """
    result = {'input': text}
    normalized = normalize(text)
    result['normalized'] = normalized
    tokens = sudachi_tokenize(normalized)
    result.update(extract_business(tokens))
    return result


def parse_person(text: str) -> dict:
    """Parse a Japanese person name into family/given name components.

    Returns a dict with keys: input, family_name, given_name,
    family_name_kana, given_name_kana, normalized.
    """
    result = {'input': text}
    normalized = normalize(text)
    result['normalized'] = normalized
    tokens = sudachi_tokenize(normalized)
    result.update(parse_person_tokens(normalized, tokens))
    return result


def corporate_parser(text: str) -> dict:
    """Deprecated alias for parse_corporate(). Will be removed in v2.0."""
    warnings.warn(
        "corporate_parser() is deprecated and will be removed in v2.0. "
        "Use parse_corporate() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return parse_corporate(text)


__all__ = ["parse_corporate", "parse_person", "corporate_parser"]
