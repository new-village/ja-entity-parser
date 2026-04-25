import pytest

# Import parser; we will stub out Sudachi tokenization for unit tests.
from ja_entityparser import parser


class FakeMorpheme:
    """Minimal stub for Sudachi Morpheme supporting the methods parser uses."""

    def __init__(self, surface: str, pos=(), normalized: str | None = None, reading_form: str | None = None):
        self._surface = surface
        # part_of_speech can be a tuple or list; code checks membership with `in`.
        self._pos = pos
        self._normalized = surface if normalized is None else normalized
        # Align with SudachiPy API name used in tests: reading_form
        self._reading = surface if reading_form is None else reading_form

    def surface(self) -> str:
        return self._surface

    def part_of_speech(self):
        return self._pos

    def normalized_form(self) -> str:
        return self._normalized
    
    def reading_form(self) -> str:
        return self._reading  # For simplicity, return surface as reading form


def test_parse_extracts_legal_form_and_brand_name(monkeypatch):
    text = "トヨタ自動車株式会社"
    tokens = [
        FakeMorpheme("トヨタ", reading_form="トヨタ"),
        FakeMorpheme("自動車", reading_form="ジドウシャ"),
        FakeMorpheme("株式会社", pos=("名詞", "法人種別"), normalized="株式会社"),
    ]

    monkeypatch.setattr(parser, "_sudachi_tokenize", lambda _t: tokens)

    result = parser.parse(text)

    assert result["brand_name"] == "トヨタ自動車"
    assert result.get("legal_form") == "株式会社"
    assert result.get("brand_kana") == "トヨタジドウシャ"
    assert "input" not in result


def test_parse_without_legal_form(monkeypatch):
    text = "トヨタ自動車"
    tokens = [FakeMorpheme("トヨタ"), FakeMorpheme("自動車")]

    monkeypatch.setattr(parser, "_sudachi_tokenize", lambda _t: tokens)

    result = parser.parse(text)

    assert result["brand_name"] == "トヨタ自動車"
    assert "legal_form" not in result


def test_parse_legal_form_at_beginning(monkeypatch):
    text = "合同会社東連"
    tokens = [
        FakeMorpheme("合同会社", pos=("名詞", "法人種別"), normalized="合同会社"),
        FakeMorpheme("東連", reading_form="トウレン"),
    ]

    monkeypatch.setattr(parser, "_sudachi_tokenize", lambda _t: tokens)

    result = parser.parse(text)

    assert result == {"brand_name": "東連", "legal_form": "合同会社", "brand_kana": "トウレン"}


def test_parse_legal_form_middle(monkeypatch):
    text = "株式会社日豊電機"
    tokens = [
        FakeMorpheme("株式会社", pos=("名詞", "法人種別"), normalized="株式会社"),
        FakeMorpheme("日豊", reading_form="ニッポウ"),
        FakeMorpheme("電機", reading_form="デンキ"),
    ]

    monkeypatch.setattr(parser, "_sudachi_tokenize", lambda _t: tokens)

    result = parser.parse(text)

    assert result["brand_name"] == "日豊電機"
    assert result.get("legal_form") == "株式会社"
    assert result.get("brand_kana") == "ニッポウデンキ"
