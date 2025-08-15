
# ja-entity-parser  
[![tests](https://github.com/new-village/ja-entity-parser/actions/workflows/tests.yml/badge.svg)](https://github.com/new-village/ja-entity-parser/actions/workflows/tests.yml) ![PyPI - Version](https://img.shields.io/pypi/v/ja_entityparser)
  
[日本語](./README_ja.md) / [English](../README.md)  
  
## 概要

`ja-entity-parser`は、日本語の企業名・法人名・個人名・住所などのエンティティを正規化・抽出するPythonライブラリです。  
SudachiPy形態素解析と独自の正規化ルール（旧字→新字、括弧・句読点・制御文字の統一など）を組み合わせ、企業名や法人種別（株式会社、合同会社など）を高精度で抽出します。

### 主な特徴

- **日本語テキストの正規化**: 旧字→新字変換、括弧・句読点・制御文字の統一、NFKC正規化、独自辞書による置換
- **企業名・法人種別抽出**: SudachiPyによる形態素解析と品詞情報を活用
- **カタカナ読み出力**: 形態素の読みを連結して `brand_kana` を生成
- **ユーザー辞書対応**: Sudachi用ユーザー辞書で業界固有語も対応可能
- **テスト・拡張性**: pytestによるユニットテスト完備

### インストール

```bash
git clone https://github.com/new-village/ja-entity-parser.git
cd ja-entity-parser
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 使い方

#### 1. 法人名抽出（正規化＋解析）

```python
from ja_entityparser import corporate_parser

result = corporate_parser("トヨタ自動車株式会社")
print(result)
# {'input': 'トヨタ自動車株式会社', 'legal_form': '株式会社', 'brand_name': 'トヨタ自動車', 'brand_kana': 'トヨタジドウシャ'}
```

#### 2. 正規化のみ

```python
from ja_entityparser.normalizer import normalize

text = "〔トヨタ〕株式会社"
print(normalize(text))
# (トヨタ)株式会社
```

#### 3. 解析のみ（正規化済みテキストを渡す）

```python
from ja_entityparser.parser import parse

result = parse("トヨタ自動車株式会社")
print(result)
# {'legal_form': '株式会社', 'brand_name': 'トヨタ自動車', 'brand_kana': 'トヨタジドウシャ'}
```

### API

- `corporate_parser(text: str) -> dict`
	- 入力文字列を正規化＋解析し、`{'input': ..., 'legal_form': ..., 'brand_name': ..., 'brand_kana': ...}` を返す（brand_kana は取得できる場合）
- `normalize(text: str) -> str`
	- 日本語テキストを正規化
- `parse(text: str) -> dict`
	- 形態素解析し、企業名・法人種別（および可能なら brand_kana）を抽出

### ライセンス

Apache License 2.0
