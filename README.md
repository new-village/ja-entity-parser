
# ja-entity-parser  
[![Test](https://github.com/new-village/ja-entity-parser/actions/workflows/test.yaml/badge.svg)](https://github.com/new-village/ja-entity-parser/actions/workflows/test.yaml) [![PyPI - Version](https://img.shields.io/pypi/v/ja-entity-parser)](https://pypi.org/project/ja-entity-parser/)
  
[日本語](./docs/README_ja.md) / [English](./README.md)  
  

## Overview

`ja-entity-parser` is a Python library for normalization and extraction of Japanese entities: corporate names, personal names, and addresses.  
It combines SudachiPy morphological analysis with custom normalization rules (old/new kanji conversion, kanji numeral conversion, bracket/punctuation/control character unification, NFKC, and user dictionary replacements) to accurately parse Japanese text into structured components.

### Features

- **Japanese text normalization**: Old/new kanji conversion, kanji numeral → Arabic, bracket/punctuation/control character unification, NFKC, corporate abbreviation expansion (`(株)` → `株式会社`, etc.)
- **Corporate name parsing**: Legal form extraction and brand name/kana via SudachiPy
- **Personal name parsing**: Family/given name split using SudachiPy POS, whitespace, or surname dictionary
- **Address parsing**: State (prefecture) → city → suburb (town) → house_number (block) using Address Base Registry data; block numbers are normalized to canonical form (halfwidth digits and hyphens). Field names follow [libpostal](https://github.com/openvenues/libpostal) label conventions
- **User dictionary support**: Extendable for industry-specific terms
- **Testing**: 66 pytest-based unit and integration tests

### Installation

```bash
pip install ja-entity-parser
```

### Usage

#### 1. Parse corporate name

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

# Abbreviations are automatically expanded:
result = parse_corporate("(株)ソフトバンク")
# normalized: '株式会社ソフトバンク'
```

#### 2. Parse person name

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

#### 3. Parse address

The parser splits an address into `state`, `city`, `suburb`, and `house_number` using the Japanese government's [Address Base Registry](https://dataset.address-br.digital.go.jp/). Field names follow [libpostal](https://github.com/openvenues/libpostal) label conventions for cross-language address matching. Block numbers are normalized to a canonical halfwidth-digit-and-hyphen form regardless of the input style (fullwidth digits, `丁目/番/号`, `番地の`, etc.). The original block string is preserved in `house_number_raw` for auditing.

```python
from ja_entityparser import parse_address

# Example 1: fullwidth digits and hyphens → normalized to halfwidth
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

# Example 2: 番地の format
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

Address data is sourced from the Japanese government's
[アドレス・ベース・レジストリ](https://dataset.address-br.digital.go.jp/) (Address Base Registry).

#### 4. Normalization only

```python
from ja_entityparser.normalizer import normalize

text = "〔トヨタ〕(株)テスト 三百二十一号"
print(normalize(text))
# (トヨタ)株式会社テスト 321号
```

### API Reference

| Function | Description | Returns |
|---|---|---|
| `parse_corporate(text)` | Parse Japanese corporate name | `input`, `normalized`, `legal_form`?, `brand_name`, `brand_kana` |
| `parse_person(text)` | Parse Japanese person name | `input`, `normalized`, `family_name`?, `given_name`?, `*_kana`? |
| `parse_address(text)` | Parse Japanese address | `input`, `normalized`, `state`?, `city`?, `suburb`?, `house_number`?, `house_number_raw`? |
| `normalize(text)` | Normalize Japanese text | `str` |

### License

Apache License 2.0
