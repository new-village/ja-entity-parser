import pytest
from ja_entityparser.parsers import person as person_mod
from ja_entityparser.parsers.person import parse_person_tokens


class FakeMorpheme:
    def __init__(self, surface, pos=(), reading_form=None):
        self._surface = surface
        self._pos = pos
        self._reading = reading_form or surface

    def surface(self):
        return self._surface

    def part_of_speech(self):
        return self._pos

    def reading_form(self):
        return self._reading

    def normalized_form(self):
        return self._surface


# ── SudachiPy POS ベースの分割 ──────────────────────────────────────────────

def test_sudachi_family_given_split():
    tokens = [
        FakeMorpheme("田中", pos=("名詞", "固有名詞", "人名-姓"), reading_form="タナカ"),
        FakeMorpheme("太郎", pos=("名詞", "固有名詞", "人名-名"), reading_form="タロウ"),
    ]
    result = parse_person_tokens("田中太郎", tokens)
    assert result["family_name"] == "田中"
    assert result["given_name"] == "太郎"
    assert result["family_name_kana"] == "タナカ"
    assert result["given_name_kana"] == "タロウ"


def test_sudachi_family_only():
    tokens = [
        FakeMorpheme("佐藤", pos=("名詞", "固有名詞", "人名-姓"), reading_form="サトウ"),
    ]
    result = parse_person_tokens("佐藤", tokens)
    assert result["family_name"] == "佐藤"
    assert result["family_name_kana"] == "サトウ"
    assert "given_name" not in result


def test_sudachi_multiple_tokens():
    tokens = [
        FakeMorpheme("山田", pos=("名詞", "固有名詞", "人名-姓"), reading_form="ヤマダ"),
        FakeMorpheme("花子", pos=("名詞", "固有名詞", "人名-名"), reading_form="ハナコ"),
    ]
    result = parse_person_tokens("山田花子", tokens)
    assert result["family_name"] == "山田"
    assert result["given_name"] == "花子"


# ── スペース区切り fallback ──────────────────────────────────────────────────

def test_space_split_fallback(monkeypatch):
    """When Sudachi returns no person POS, fall back to space split."""
    tokens = [
        FakeMorpheme("田中", pos=()),
        FakeMorpheme("太郎", pos=()),
    ]
    monkeypatch.setattr(person_mod, "_split_by_sudachi", lambda t: None)
    result = parse_person_tokens("田中 太郎", tokens)
    assert result["family_name"] == "田中"
    assert result["given_name"] == "太郎"


# ── 姓辞書 fallback ─────────────────────────────────────────────────────────

def test_dict_fallback(monkeypatch):
    """When no space, fall back to surname dictionary lookup."""
    tokens = [FakeMorpheme("鈴木一郎", pos=())]
    monkeypatch.setattr(person_mod, "_split_by_sudachi", lambda t: None)
    monkeypatch.setattr(person_mod, "_split_by_space", lambda t: None)
    result = parse_person_tokens("鈴木一郎", tokens)
    assert result["family_name"] == "鈴木"
    assert result["given_name"] == "一郎"


# ── parse_person 統合 ────────────────────────────────────────────────────────

def test_parse_person_api():
    from ja_entityparser import parse_person
    result = parse_person("田中太郎")
    assert result["input"] == "田中太郎"
    assert "normalized" in result
    # At minimum, one of family_name or given_name should be present
    # (exact split depends on Sudachi dictionary)
    assert "family_name" in result or "given_name" in result
