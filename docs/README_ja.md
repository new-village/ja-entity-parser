# ja-entity-parser  
[![Test](https://github.com/new-village/ja-entity-parser/actions/workflows/test.yaml/badge.svg)](https://github.com/new-village/ja-entity-parser/actions/workflows/test.yaml) [![PyPI - Version](https://img.shields.io/pypi/v/ja-entity-parser)](https://pypi.org/project/ja-entity-parser/)
  
[日本語](./README_ja.md) / [English](../README.md)  
  
## 概要

`ja-entity-parser` は、日本語の企業名・個人名・住所などのエンティティを正規化・抽出する Python ライブラリです。  
SudachiPy による形態素解析と独自の正規化ルール（旧字→新字変換、漢数字→算用数字変換、括弧・句読点・制御文字の統一、NFKC、ユーザー辞書置換）を組み合わせ、日本語テキストを構造化された各コンポーネントに高精度で分解します。

### 主な特徴

- **日本語テキスト正規化**: 旧字→新字変換、漢数字→算用数字変換、括弧・句読点・制御文字の統一、NFKC正規化、法人略称の展開（`(株)` → `株式会社` など）
- **企業名解析**: SudachiPy による法人種別抽出とブランド名・カナの取得
- **個人名解析**: SudachiPy の品詞情報・スペース・苗字辞書を使った姓名分割
- **住所解析**: アドレス・ベース・レジストリデータによる state（都道府県）→ city（市区町村）→ suburb（町名）→ house_number（番地）の分割。フィールド名は [libpostal](https://github.com/openvenues/libpostal) のラベル規約に準拠。番地は半角数字＋ハイフンの正規形に統一
- **ユーザー辞書対応**: Sudachi ユーザー辞書で業界固有語にも対応可能
- **テスト**: pytest によるユニット・統合テスト 66 件完備

### インストール

```bash
pip install ja-entity-parser
```

### 使い方

#### 1. 企業名解析

```python
from ja_entityparser import parse_corporate

result = parse_corporate("トヨタ自動車株式会社")
print(result)
# {
#   'input': 'トヨタ自動車株式会社',
#   'normalized': 'トヨタ自動車株式会社',
#   'legal_form': '株式会社',
#   'brand_name': 'トヨタ自動車',
#   'brand_kana': 'トヨタジドウシャ'
# }

# 略称は自動的に展開されます
result = parse_corporate("(株)ソフトバンク")
# normalized: '株式会社ソフトバンク'
```

#### 2. 個人名解析

```python
from ja_entityparser import parse_person

result = parse_person("田中 太郎")
print(result)
# {
#   'input': '田中 太郎',
#   'normalized': '田中 太郎',
#   'family_name': '田中',
#   'given_name': '太郎',
#   'family_name_kana': 'タナカ',
#   'given_name_kana': 'タロウ'
# }
```

#### 3. 住所解析

住所を `state`（都道府県）・`city`（市区町村）・`suburb`（町名）・`house_number`（番地）に分割します。フィールド名は [libpostal](https://github.com/openvenues/libpostal) のラベル規約に準拠しています。データソースは日本政府の[アドレス・ベース・レジストリ](https://dataset.address-br.digital.go.jp/)です。

番地は全角数字・`丁目/番/号`・`番地の` などの表記ゆれに対応し、半角数字＋ハイフンの正規形に変換します。正規化前の原文は `house_number_raw` に保持されます。

```python
from ja_entityparser import parse_address

# 例1: 全角数字 + 丁目/番/号 → 正規化されてハイフン区切りに
result = parse_address("北海道札幌市中央区大通西３丁目１番５号")
print(result)
# {
#   'input': '北海道札幌市中央区大通西３丁目１番５号',
#   'normalized': '北海道札幌市中央区大通西3丁目1番5号',
#   'state': '北海道',
#   'city': '札幌市中央区',
#   'suburb': '大通西',
#   'house_number': '3-1-5',
#   'house_number_raw': '3丁目1番5号'
# }

# 例2: 番地の 形式
result = parse_address("愛知県江南市大字小折６２８番地の１")
print(result)
# {
#   'input': '愛知県江南市大字小折６２８番地の１',
#   'normalized': '愛知県江南市大字小折628番地の1',
#   'state': '愛知県',
#   'city': '江南市',
#   'suburb': '大字小折',
#   'house_number': '628-1',
#   'house_number_raw': '628番地の1'
# }
```

#### 4. 正規化のみ

```python
from ja_entityparser.normalizer import normalize

text = "〔トヨタ〕(株)テスト 三百二十一号"
print(normalize(text))
# (トヨタ)株式会社テスト 321号
```

### API リファレンス

| 関数 | 説明 | 返却フィールド |
|---|---|---|
| `parse_corporate(text)` | 企業名を解析 | `input`, `normalized`, `legal_form`?, `brand_name`, `brand_kana` |
| `parse_person(text)` | 個人名を解析 | `input`, `normalized`, `family_name`?, `given_name`?, `*_kana`? |
| `parse_address(text)` | 住所を解析 | `input`, `normalized`, `state`?, `city`?, `suburb`?, `house_number`?, `house_number_raw`? |
| `normalize(text)` | 日本語テキストを正規化 | `str` |

### ライセンス

Apache License 2.0
