
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
- **Address parsing**: Prefecture → city → town → block using Address Base Registry data
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

```python
from ja_entityparser import parse_address

result = parse_address("東京都台東区寿3-1-5")
print(result)
# {
#   'input': '東京都台東区寿3-1-5',
#   'normalized': '東京都台東区寿3-1-5',
#   'prefecture': '東京都',
#   'city': '台東区',
#   'town': '寿',
#   'block': '3-1-5'
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
| `parse_address(text)` | Parse Japanese address | `input`, `normalized`, `prefecture`?, `city`?, `town`?, `block`? |
| `normalize(text)` | Normalize Japanese text | `str` |

### License

Apache License 2.0
