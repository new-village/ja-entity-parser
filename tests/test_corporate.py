import pytest

from ja_entityparser.parsers import corporate as corporate_mod
from ja_entityparser.parsers.corporate import extract_business
from ja_entityparser import tokenizer as tokenizer_mod


class FakeMorpheme:
    """Minimal stub for Sudachi Morpheme."""

    def __init__(self, surface: str, pos=(), normalized: str | None = None, reading_form: str | None = None):
        self._surface = surface
        self._pos = pos
        self._normalized = surface if normalized is None else normalized
        self._reading = surface if reading_form is None else reading_form

    def surface(self) -> str:
        return self._surface

    def part_of_speech(self):
        return self._pos

    def normalized_form(self) -> str:
        return self._normalized

    def reading_form(self) -> str:
        return self._reading


def test_parse_extracts_legal_form_and_brand_name(monkeypatch):
    tokens = [
        FakeMorpheme("トヨタ", reading_form="トヨタ"),
        FakeMorpheme("自動車", reading_form="ジドウシャ"),
        FakeMorpheme("株式会社", pos=("名詞", "法人種別"), normalized="株式会社"),
    ]

    result = extract_business(tokens)

    assert result["brand_name"] == "トヨタ自動車"
    assert result.get("legal_form") == "株式会社"
    assert result.get("brand_kana") == "トヨタジドウシャ"
    assert "input" not in result


def test_parse_without_legal_form():
    tokens = [FakeMorpheme("トヨタ"), FakeMorpheme("自動車")]

    result = extract_business(tokens)

    assert result["brand_name"] == "トヨタ自動車"
    assert "legal_form" not in result


def test_parse_legal_form_at_beginning():
    tokens = [
        FakeMorpheme("合同会社", pos=("名詞", "法人種別"), normalized="合同会社"),
        FakeMorpheme("東連", reading_form="トウレン"),
    ]

    result = extract_business(tokens)

    assert result == {"brand_name": "東連", "legal_form": "合同会社", "brand_kana": "トウレン"}


def test_parse_legal_form_middle():
    tokens = [
        FakeMorpheme("株式会社", pos=("名詞", "法人種別"), normalized="株式会社"),
        FakeMorpheme("日豊", reading_form="ニッポウ"),
        FakeMorpheme("電機", reading_form="デンキ"),
    ]

    result = extract_business(tokens)

    assert result["brand_name"] == "日豊電機"
    assert result.get("legal_form") == "株式会社"
    assert result.get("brand_kana") == "ニッポウデンキ"
