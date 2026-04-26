import logging
from .normalizer import normalize, normalize_address
from .tokenizer import sudachi_tokenize
from .parsers.corporate import extract_business
from .parsers.person import parse_person_tokens
from .parsers.address import parse_address_text

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


def parse_address(text: str) -> dict:
    """Parse a Japanese address into state, city, suburb, and house_number.

    Returns a dict with keys: input, normalized, and any of:
    state, city, suburb, house_number, house_number_raw.

    Field names follow libpostal label conventions for cross-language compatibility.
    Uses normalize_address() instead of normalize() to preserve kanji numerals
    in place names (e.g. 千葉県, 三重県, 千代田区).
    """
    result = {'input': text}
    normalized = normalize_address(text)
    result['normalized'] = normalized
    result.update(parse_address_text(normalized))
    return result


__all__ = ["parse_corporate", "parse_person", "parse_address"]
