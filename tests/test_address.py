import pytest
from ja_entityparser.parsers.address import parse_address_text
from ja_entityparser.parsers.address_normalize import normalize_block
from ja_entityparser import parse_address


# ── 基本ケース ────────────────────────────────────────────────────────────────

def test_tokyo_taito_full():
    result = parse_address_text("東京都台東区寿3-1-5")
    assert result["state"] == "東京都"
    assert result["city"] == "台東区"
    assert result["suburb"] == "寿"
    assert result["house_number"] == "3-1-5"


def test_osaka_city():
    result = parse_address_text("大阪府大阪市北区梅田1-2-3")
    assert result["state"] == "大阪府"
    assert result["city"] == "大阪市北区"
    assert result.get("house_number") == "1-2-3"


def test_kanagawa_yokohama():
    result = parse_address_text("神奈川県横浜市中区山下町1-1")
    assert result["state"] == "神奈川県"
    assert result["city"] == "横浜市中区"
    assert result.get("house_number") is not None


def test_hokkaido_sapporo():
    # 丁目/番/号 → normalized to 1-1-1
    result = parse_address_text("北海道札幌市中央区大通西1丁目1番1号")
    assert result["state"] == "北海道"
    assert result["city"] == "札幌市中央区"
    assert result["house_number"] == "1-1-1"


def test_no_block():
    result = parse_address_text("東京都渋谷区")
    assert result["state"] == "東京都"
    assert result["city"] == "渋谷区"
    assert "house_number" not in result


def test_prefecture_only():
    result = parse_address_text("沖縄県")
    assert result["state"] == "沖縄県"
    assert "city" not in result
    assert "house_number" not in result


# ── parse_address 公開API ─────────────────────────────────────────────────────

def test_parse_address_api():
    result = parse_address("東京都台東区寿3-1-5")
    assert result["input"] == "東京都台東区寿3-1-5"
    assert "normalized" in result
    assert result["state"] == "東京都"
    assert result["city"] == "台東区"
    assert result["house_number"] == "3-1-5"


def test_parse_address_aichi():
    result = parse_address("愛知県名古屋市中区三の丸3-1-2")
    assert result["state"] == "愛知県"
    assert result["city"] == "名古屋市中区"
    assert "house_number" in result


# ── ブロック正規化: normalize_block 単体テスト ────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    # 全角数字 + 全角ハイフン
    ("３－１－５",           "3-1-5"),
    # 丁目/番/号
    ("３丁目１番５号",       "3-1-5"),
    ("1丁目1番1号",          "1-1-1"),
    ("10丁目2番",            "10-2"),
    # 番地の
    ("３番地の１",           "3-1"),
    ("６２８番地の１",       "628-1"),
    # 番地 (terminal)
    ("１２番地",             "12"),
    ("12番地",               "12"),
    # 番号
    ("５番３号",             "5-3"),
    ("5番3号",               "5-3"),
    # すでに正規形
    ("3-1-5",                "3-1-5"),
    ("1-2",                  "1-2"),
    # の
    ("３の１",               "3-1"),
    # 全角数字のみハイフン区切り
    ("１２３－４５",         "123-45"),
])
def test_normalize_block(raw, expected):
    assert normalize_block(raw) == expected


# ── ブロック正規化: parse_address_text の block フィールド ───────────────────

@pytest.mark.parametrize("address,expected_block", [
    # 全角ハイフン区切り
    ("東京都台東区寿３－１－５",            "3-1-5"),
    # 丁目/番/号 形式
    ("北海道札幌市中央区大通西３丁目１番５号", "3-1-5"),
    # 番地の形式
    ("愛知県江南市大字小折６２８番地の１",   "628-1"),
    # 半角数字ハイフン (already canonical)
    ("大阪府大阪市北区梅田1-2-3",           "1-2-3"),
    # 番地 terminal
    ("東京都渋谷区代々木2番地",             "2"),
])
def test_parse_address_block_normalized(address, expected_block):
    result = parse_address_text(address)
    assert result.get("house_number") == expected_block, (
        f"address={address!r}, got house_number={result.get('house_number')!r}, expected={expected_block!r}"
    )


def test_block_raw_preserved():
    """house_number_raw should contain the original extracted string."""
    result = parse_address_text("東京都台東区寿３－１－５")
    assert result.get("house_number") == "3-1-5"
    assert result.get("house_number_raw") == "３－１－５"
