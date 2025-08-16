import pytest
import unicodedata
import joyokanji
from ja_entityparser.normalizer import normalize

# 制御・不可視文字の除去
@pytest.mark.parametrize("input_text,expected", [
    ("ゼロ\u200B幅\u2060スペース", "ゼロ幅スペース"),
    ("テスト\uFEFF", "テスト"),
    ("\u00ADテスト", "テスト"),
])
def test_remove_controls(input_text, expected):
    assert normalize(input_text) == expected

# 括弧→丸括弧
@pytest.mark.parametrize("input_text,expected", [
    ("《引用》「括弧」を(スペース)に！", "(引用)(括弧)を(スペース)に!"),
    ("【テスト】", "(テスト)"),
    ("｛サンプル｝", "(サンプル)"),
])
def test_brackets_to_space(input_text, expected):
    assert normalize(input_text) == expected

# 句読点・中点→スペース
@pytest.mark.parametrize("input_text,expected", [
    ("テスト、サンプル。・･，．", "テスト サンプル"),
    ("abc, def; ghi: jkl! mno?", "abc def ghi jkl mno"),
])
def test_punct_to_space(input_text, expected):
    assert normalize(input_text) == expected

# ハイフン/ダッシュ & チルダ/波ダッシュの統一
@pytest.mark.parametrize("input_text,expected", [
    ("—–―‐ｰー", "----ーー"),
    ("テスト〜サンプル～", "テスト~サンプル~"),
])
def test_hyphen_tilde_choon(input_text, expected):
    assert normalize(input_text) == expected

# 濁点/半濁点（非合成）→ 結合記号
@pytest.mark.parametrize("input_text,expected", [
    ("ｶ）ｻﾝﾌ\u309Bﾙ ／ ﾊ\u309C", "カ)サンブル / パ"),
])
def test_voicing_map(input_text, expected):
    assert normalize(input_text) == expected

# joyokanji 旧字→新字
@pytest.mark.parametrize("input_text,expected", [
    ("髙島屋株式會社", "高島屋株式会社"),
    ("髙﨑隆杜", "高崎隆杜"),
])
def test_joyokanji(input_text, expected):
    assert normalize(input_text) == expected

# 英字は小文字化
@pytest.mark.parametrize("input_text,expected", [
    ("ＡＢＣ（株）テスト・カンパニー", "ABC(株)テスト カンパニー"),
    ("Microsoft Corporation", "Microsoft Corporation"),
])
def test_lowercase(input_text, expected):
    assert normalize(input_text) == expected

# NFKC正規化
@pytest.mark.parametrize("input_text,expected", [
    ("㍿ＡＢＣ", "株式会社ABC"),
    ("日本ﾏｲｸﾛｿﾌﾄ㈱", "日本マイクロソフト(株)"),
])
def test_nfkc(input_text, expected):
    assert normalize(input_text) == expected

# 連続スペース圧縮
@pytest.mark.parametrize("input_text,expected", [
    ("テスト   サンプル", "テスト サンプル"),
    ("  テスト\nサンプル  ", "テスト サンプル"),
])
def test_space_compression(input_text, expected):
    assert normalize(input_text) == expected

# normalize.jsonによる置換
@pytest.mark.parametrize("input_text,expected", [
    ("会杜", "会社"),
    ("これは会杜です", "これは会社です"),
    ("会杜と会杜", "会社と会社"),
])
def test_normalize_json_replace(input_text, expected):
    assert normalize(input_text) == expected

# サンプルの網羅
@pytest.mark.parametrize("input_text,expected", [
    ("ＡＢＣ（株）テスト・カンパニー 〜 第１事業部", "ABC(株)テスト カンパニー ~ 第1事業部")
])
def test_samples(input_text, expected):
    assert normalize(input_text) == expected
