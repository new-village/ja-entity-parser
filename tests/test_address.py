import pytest
from ja_entityparser.parsers.address import parse_address_text
from ja_entityparser import parse_address


# ── 基本ケース ────────────────────────────────────────────────────────────────

def test_tokyo_taito_full():
    result = parse_address_text("東京都台東区寿3-1-5")
    assert result["prefecture"] == "東京都"
    assert result["city"] == "台東区"
    assert result["town"] == "寿"
    assert result["block"] == "3-1-5"


def test_osaka_city():
    result = parse_address_text("大阪府大阪市北区梅田1-2-3")
    assert result["prefecture"] == "大阪府"
    assert result["city"] == "大阪市"
    assert result.get("block") == "1-2-3"


def test_kanagawa_yokohama():
    result = parse_address_text("神奈川県横浜市中区山下町1-1")
    assert result["prefecture"] == "神奈川県"
    assert result["city"] == "横浜市"
    assert result.get("block") is not None


def test_hokkaido_sapporo():
    result = parse_address_text("北海道札幌市中央区大通西1丁目1番1号")
    assert result["prefecture"] == "北海道"
    assert result["city"] == "札幌市"
    assert "1丁目1番1号" in result.get("block", "")


def test_no_block():
    result = parse_address_text("東京都渋谷区")
    assert result["prefecture"] == "東京都"
    assert result["city"] == "渋谷区"
    assert "block" not in result


def test_prefecture_only():
    result = parse_address_text("沖縄県")
    assert result["prefecture"] == "沖縄県"
    assert "city" not in result
    assert "block" not in result


# ── parse_address 公開API ─────────────────────────────────────────────────────

def test_parse_address_api():
    result = parse_address("東京都台東区寿3-1-5")
    assert result["input"] == "東京都台東区寿3-1-5"
    assert "normalized" in result
    assert result["prefecture"] == "東京都"
    assert result["city"] == "台東区"
    assert result["block"] == "3-1-5"


def test_parse_address_aichi():
    result = parse_address("愛知県名古屋市中区三の丸3-1-2")
    assert result["prefecture"] == "愛知県"
    assert result["city"] == "名古屋市"
    assert "block" in result
