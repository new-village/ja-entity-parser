
# ja-entity-parser  
[![Test](https://github.com/new-village/ja-entity-parser/actions/workflows/test.yaml/badge.svg)](https://github.com/new-village/ja-entity-parser/actions/workflows/test.yaml) [![PyPI - Version](https://img.shields.io/pypi/v/ja-entity-parser)](https://pypi.org/project/ja-entity-parser/)
  
[日本語](./docs/README_ja.md) / [English](./README.md)  
  

## Overview

`ja-entity-parser` is a Python library for normalization and extraction of Japanese entities such as company names, corporate types, personal names, and addresses.  
It combines SudachiPy morphological analysis with custom normalization rules (old/new kanji conversion, bracket/punctuation/control character unification, NFKC, and user dictionary replacements) to accurately extract brand names and legal forms (e.g., 株式会社, 合同会社).

### Features

- **Japanese text normalization**: Old/new kanji conversion, bracket/punctuation/control character unification, NFKC, custom dictionary replacements
- **Company/corporate type extraction**: Uses SudachiPy and part-of-speech info
- **Katakana reading output**: Builds brand_kana by concatenating token reading forms
- **User dictionary support**: Extendable for industry-specific terms
- **Testing & extensibility**: Comes with pytest-based unit tests

### Installation

```bash
pip install ja-entity-parser
```

### Usage

#### 1. Extract company/corporate info (normalize + parse)

```python
from ja_entityparser import corporate_parser

result = corporate_parser("トヨタ自動車株式会社")
print(result)
# {'input': 'トヨタ自動車株式会社', 'legal_form': '株式会社', 'brand_name': 'トヨタ自動車', 'brand_kana': 'トヨタジドウシャ'}
```

#### 2. Normalization only

```python
from ja_entityparser.normalizer import normalize

text = "〔トヨタ〕株式会社"
print(normalize(text))
# (トヨタ)株式会社
```

#### 3. Parsing only (pass normalized text)

```python
from ja_entityparser.parser import parse

result = parse("トヨタ自動車株式会社")
print(result)
# {'legal_form': '株式会社', 'brand_name': 'トヨタ自動車', 'brand_kana': 'トヨタジドウシャ'}
```

### API

- `corporate_parser(text: str) -> dict`
	- Normalize and parse input, returns `{'input': ..., 'legal_form': ..., 'brand_name': ..., 'brand_kana': ...}` (brand_kana when available)
- `normalize(text: str) -> str`
	- Normalize Japanese text
- `parse(text: str) -> dict`
	- Morphological analysis and extraction of brand name/legal form (and brand_kana when available)

### License

Apache License 2.0