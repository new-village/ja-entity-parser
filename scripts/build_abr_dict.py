#!/usr/bin/env python3
"""
Build address_parts.json from Geolonia japanese-addresses-v2 API (based on ABR data).

Data source: https://japanese-addresses-v2.geoloniamaps.com/api/ja.json
This dataset is derived from the Address Base Registry (ABR / アドレス・ベース・レジストリ)
maintained by Japan's Digital Agency.

v2 schema (per pref entry):
  {
    "pref": "北海道",
    "cities": [
      { "city": "札幌市", "ward": "中央区" },          # 政令指定都市の区
      { "city": "函館市" },                             # 一般市
      { "county": "石狩郡", "city": "当別町" },         # 郡+町村
      ...
    ]
  }

Output format:
{
  "prefectures": ["北海道", "青森県", ...],  // 47 prefectures
  "municipalities": {
    "北海道": ["札幌市中央区", "石狩郡当別町", "函館市", ...],
    ...
  }
}

Requirements:
- Seirei-shitei-toshi wards as full path (e.g. "大阪市北区", not "北区")
- Gun+town as full path (e.g. "築上郡築上町")
- Deduplicated
- Sorted by length descending within each prefecture (longest-match-first for parser)
"""

import json
import sys
import urllib.request
from pathlib import Path

GEOLONIA_V2_URL = "https://japanese-addresses-v2.geoloniamaps.com/api/ja.json"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "ja_entityparser" / "dict" / "address_parts.json"

# Canonical prefecture order
PREFECTURE_ORDER = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
    "岐阜県", "静岡県", "愛知県", "三重県",
    "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
    "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県",
    "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
]


def fetch_v2_data(local_path=None):
    """Fetch from Geolonia v2 API or use local cache."""
    if local_path and Path(local_path).exists():
        print(f"Using local cache: {local_path}")
        with open(local_path, encoding="utf-8") as f:
            raw = json.load(f)
        return raw["data"] if isinstance(raw, dict) and "data" in raw else raw

    print(f"Fetching from {GEOLONIA_V2_URL} ...")
    req = urllib.request.Request(GEOLONIA_V2_URL)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    # v2 wraps in { meta, data: [...] }
    data = raw["data"] if isinstance(raw, dict) and "data" in raw else raw
    print(f"Fetched {len(data)} prefecture entries")
    return data


def build_municipality_name(city_entry):
    """
    Convert a v2 city entry into a display string.

    Cases:
      { city, ward }    → "{city}{ward}"          e.g. 札幌市中央区
      { county, city }  → "{county}{city}"        e.g. 石狩郡当別町
      { city }          → "{city}"                e.g. 函館市
    """
    city = city_entry.get("city", "")
    ward = city_entry.get("ward", "")
    county = city_entry.get("county", "")

    if ward:
        return f"{city}{ward}"
    if county:
        return f"{county}{city}"
    return city


def build_dict(v2_data):
    """Build address_parts dict from v2 data list."""
    # Build a lookup: pref_name → list of municipality strings
    pref_map = {}
    for entry in v2_data:
        pref = entry.get("pref", "")
        cities = entry.get("cities", [])
        names = [build_municipality_name(c) for c in cities]
        pref_map[pref] = names

    prefectures = []
    municipalities = {}

    for pref in PREFECTURE_ORDER:
        if pref not in pref_map:
            print(f"WARNING: {pref} not found in source data", file=sys.stderr)
            continue
        prefectures.append(pref)
        # Deduplicate and sort by length descending (longest-match-first)
        names = sorted(set(pref_map[pref]), key=lambda x: (-len(x), x))
        municipalities[pref] = names

    return {"prefectures": prefectures, "municipalities": municipalities}


def main():
    local_cache = "/tmp/geolonia_v2_ja.json"
    v2_data = fetch_v2_data(local_cache)

    result = build_dict(v2_data)

    # Stats
    total_muni = sum(len(v) for v in result["municipalities"].values())
    print(f"\nGenerated dictionary:")
    print(f"  Prefectures: {len(result['prefectures'])}")
    print(f"  Total municipalities: {total_muni}")

    # Sample check
    hokkaido = result["municipalities"].get("北海道", [])
    print(f"  北海道 sample (first 5): {hokkaido[:5]}")
    osaka = result["municipalities"].get("大阪府", [])
    print(f"  大阪府 sample (first 5): {osaka[:5]}")

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nWritten to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
