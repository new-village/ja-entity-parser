"""Integration tests for all three parsers end-to-end."""
import pytest
from ja_entityparser import parse_corporate, parse_person, parse_address


# ── parse_corporate ───────────────────────────────────────────────────────────

class TestParseCorporate:
    def test_toyota(self):
        r = parse_corporate("トヨタ自動車株式会社")
        assert r["input"] == "トヨタ自動車株式会社"
        assert "normalized" in r
        assert r.get("legal_form") == "株式会社"

    def test_abbreviation_normalization(self):
        r = parse_corporate("(株)ソフトバンク")
        assert r["input"] == "(株)ソフトバンク"
        # After normalization (株) → 株式会社
        assert "株式会社" in r["normalized"]

    def test_godo_kaisha(self):
        r = parse_corporate("合同会社サンプル商事")
        assert r.get("legal_form") == "合同会社"

    def test_no_legal_form(self):
        r = parse_corporate("グーグル")
        assert r["input"] == "グーグル"
        assert "brand_name" in r

    def test_old_kanji_normalized(self):
        r = parse_corporate("髙島屋株式會社")
        assert "高島屋" in r["normalized"]
        assert "株式会社" in r["normalized"]


# ── parse_person ──────────────────────────────────────────────────────────────

class TestParsePerson:
    def test_space_separated(self):
        r = parse_person("田中 太郎")
        assert r["input"] == "田中 太郎"
        assert "normalized" in r
        assert r["family_name"] == "田中"
        assert r["given_name"] == "太郎"

    def test_dict_fallback_suzuki(self):
        r = parse_person("鈴木一郎")
        assert r["input"] == "鈴木一郎"
        assert "family_name" in r or "given_name" in r

    def test_sato_hanako(self):
        r = parse_person("佐藤 花子")
        assert r["family_name"] == "佐藤"
        assert r["given_name"] == "花子"

    def test_input_preserved(self):
        r = parse_person("山田太郎")
        assert r["input"] == "山田太郎"
        assert "normalized" in r

    def test_returns_dict(self):
        r = parse_person("中村健二")
        assert isinstance(r, dict)


# ── parse_address ─────────────────────────────────────────────────────────────

class TestParseAddress:
    def test_tokyo_taito(self):
        r = parse_address("東京都台東区寿3-1-5")
        assert r["input"] == "東京都台東区寿3-1-5"
        assert r["prefecture"] == "東京都"
        assert r["city"] == "台東区"
        assert r["town"] == "寿"
        assert r["block"] == "3-1-5"

    def test_osaka(self):
        r = parse_address("大阪府大阪市北区梅田1-2-3")
        assert r["prefecture"] == "大阪府"
        assert r["city"] == "大阪市"
        assert r.get("block") == "1-2-3"

    def test_hokkaido_chome(self):
        r = parse_address("北海道札幌市中央区大通西1丁目1番1号")
        assert r["prefecture"] == "北海道"
        assert r["city"] == "札幌市"
        assert "1丁目1番1号" in r.get("block", "")

    def test_normalized_field(self):
        r = parse_address("東京都渋谷区神南1-1-1")
        assert "normalized" in r
        assert r["prefecture"] == "東京都"

    def test_full_roundtrip_aichi(self):
        r = parse_address("愛知県名古屋市千種区今池1-1-10")
        assert r["prefecture"] == "愛知県"
        assert r["city"] == "名古屋市"
        assert "block" in r



