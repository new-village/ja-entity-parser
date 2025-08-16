import re
import joyokanji  # pip install joyokanji
import unicodedata
import json
import os
import logging

logger = logging.getLogger(__name__)

# ====== 1) 制御・不可視文字の除去 ======
# ※ NFKC では消えないことがあるため先に除去
CONTROL_CHARS = [
    "\u200B",  # ZERO WIDTH SPACE
    "\u200C",  # ZERO WIDTH NON-JOINER
    "\u200D",  # ZERO WIDTH JOINER
    "\u2060",  # WORD JOINER
    "\uFEFF",  # ZERO WIDTH NO-BREAK SPACE (BOM)
    "\u00AD",  # SOFT HYPHEN
]

CONTROL_PATTERN = re.compile("|".join(map(re.escape, CONTROL_CHARS)))

# ===== 括弧 → 丸括弧に統一（全角/半角/各種） =====
BRACKETS_RE = re.compile(r"[()\[\]{}（）［］｛｝〈〉《》【】「」『』‹›«»]")

# シンプルにペア定義から開き/閉じ集合を生成
BRACKET_PAIRS = [
    "()", "[]", "{}", "（）", "［］", "｛｝", "〈〉", "《》", "【】", "〔〕", "「」", "『』", "‹›", "«»",
]
OPEN_BRACKETS = {p[0] for p in BRACKET_PAIRS}
CLOSE_BRACKETS = {p[1] for p in BRACKET_PAIRS}

# ===== 句読点・中点 → スペース =====
#   ・和文：、 。 ・ ･ ， ．
#   ・欧文：, . ; : ! ? （必要なら拡張）
PUNCT_RE = re.compile(r"[、。・･，．,.;:!?]")

# ===== ハイフン/ダッシュ & チルダ/波ダッシュの統一 =====
HYPHENS = [
    "\u002D", # - hyphen-minus
    "\u2010", # ‐ hyphen
    "\u2011", # - non-breaking hyphen
    "\u2012", # ‒ figure dash
    "\u2013", # – en dash
    "\u2014", # — em dash
    "\u2015", # ― horizontal bar
    "\u2212", # − minus sign
]
TILDES = [
    "\u007E", # ~ tilde
    "\u02DC", # ˜ small tilde
    "\u223C", # ∼
    "\u301C", # 〜 wave dash
    "\uFF5E", # ～ fullwidth tilde
]
CHOON_CANDIDATES = ["\u30FC", "ｰ", "ー"]  # 長音候補（半角ｰ含む）

# ===== 濁点/半濁点（非合成）→ 結合記号（ご指定の2パターンのみ） =====
VOICING_MAP = {
    "\u309B": "\u3099",  # ゛ → COMBINING VOICED SOUND MARK
    "\u309C": "\u309A",  # ゜ → COMBINING SEMI-VOICED SOUND MARK
}

def _remove_controls(s: str) -> str:
    return CONTROL_PATTERN.sub("", s)

def _brackets_to_space(s: str) -> str:
    # 括弧はスペースではなく丸括弧に統一（開き→'(', 閉じ→')'）
    return "".join(
        "(" if ch in OPEN_BRACKETS else (")" if ch in CLOSE_BRACKETS else ch)
        for ch in s
    )

def _punct_to_space(s: str) -> str:
    return PUNCT_RE.sub(" ", s)

def _unify_hyphen_tilde_choon(s: str) -> str:
    for h in HYPHENS:
        s = s.replace(h, "-")
    for t in TILDES:
        s = s.replace(t, "~")
    for c in CHOON_CANDIDATES:
        s = s.replace(c, "ー")
    return s

def _apply_voicing_map(s: str) -> str:
    return s.translate(str.maketrans(VOICING_MAP))

def _load_normalize_dict():
    path = os.path.join(os.path.dirname(__file__), "dict", "normalize.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

_NORMALIZE_DICT = _load_normalize_dict()

def normalize(text: str) -> str:
    """
    日本語標準化（NFKCを最後）：
      - 制御/不可視文字の除去
      - 括弧→丸括弧、句読点/中点→スペース
      - ハイフン/長音/チルダの統一
      - 濁点/半濁点（U+309B/C → U+3099/A）
      - joyokanji 旧字→新字
      - 英字は小文字化
      - NFKC
      - normalize.jsonによる置換
      - 連続スペース圧縮
    """
    # 1) 制御・不可視
    text = _remove_controls(text)

    # 2) 括弧→丸括弧
    text = _brackets_to_space(text)

    # 3) 句読点/中点→スペース
    text = _punct_to_space(text)

    # 4) ハイフン/長音/チルダ統一
    text = _unify_hyphen_tilde_choon(text)

    # 5) 濁点/半濁点（指定2パターン）
    text = _apply_voicing_map(text)

    # 6) 旧字→新字（joyokanji）
    text = joyokanji.convert(text, variants=True)

    # 7) 最後に NFKC
    text = unicodedata.normalize("NFKC", text)

    # 9) normalize.jsonによる置換
    for k, v in _NORMALIZE_DICT.items():
        text = text.replace(k, v)

    # 10) 連続スペース圧縮
    text = re.sub(r"\s+", " ", text).strip()
    return text
