
from __future__ import annotations
import json
import re
from dataclasses import dataclass, asdict
from typing import Iterable, Dict, Tuple

# 0) Keyword lists
HATE_KEYWORDS = {"slur1", "slur2"}          # classroom placeholders
OFFENSIVE_KEYWORDS = {"stupid", "idiot"}    # simple examples

# Spam thresholds
MAX_LINKS_FOR_SAFE = 1       # 2+ links => spam
MAX_HASHTAGS_FOR_SAFE = 2    # 3+ hashtags => spam

# 1)  partner preprocessing (regexRules.py)
def _try_partner_preprocess(text: str):
    try:
        from regexRules import extract_all  # user's file
        return extract_all(text)
    except Exception:
        return None

# Fallback mini-preprocessor
_URL_RE = re.compile(r'(?:https?://|www\.)\S+', re.I)
_HASHTAG_RE = re.compile(r'(?<!\w)#\w+')
_MENTION_RE = re.compile(r'(?<!\w)@\w+')
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA70-\U0001FAFF"
    "]"
)
def _fallback_extract_all(text: str):
    normalized = re.sub(r'\s+', ' ', (text or "")).strip().lower()
    urls = _URL_RE.findall(normalized)
    hashtags = _HASHTAG_RE.findall(normalized)
    mentions = _MENTION_RE.findall(normalized)
    emojis = _EMOJI_RE.findall(normalized)
    tokens = normalized.split()
    return {
        "mentions": mentions, "hashtags": hashtags, "urls": urls,
        "emojis": emojis, "tokens": tokens, "normalized": normalized
    }

def preprocess(text: str):
    d = _try_partner_preprocess(text)
    if d:
        # normalize just in case
        d["normalized"] = re.sub(r'\s+', ' ', (d.get("normalized") or str(text)).lower()).strip()
        if not d.get("tokens"):
            d["tokens"] = (d.get("normalized") or "").split()
        return d
    return _fallback_extract_all(text)

# 2) Map tokens into a small alphabet
def categorize(token: str) -> str:
    # URLs and hashtags first 
    lowered = token.lower()
    if lowered.startswith("http") or lowered.startswith("www."):
        return "LINK"
    if lowered.startswith("#"):
        return "HASHTAG"

    # for example if gets: "idiot!" -> "idiot", "(stupid)" -> "stupid"
    core = re.sub(r"^[^\w]+|[^\w]+$", "", lowered)

    if core in HATE_KEYWORDS:
        return "HATE"
    if core in OFFENSIVE_KEYWORDS:
        return "OFFENSIVE"
    return "OTHER"


# 3) DFA class
@dataclass(frozen=True)
class DFA:
    states: set
    alphabet: set
    start: str
    accept: set
    delta: Dict[Tuple[str, str], str]  # (state, symbol) -> state

    def run(self, symbols):
        s = self.start
        for a in symbols:
            s = self.delta.get((s, a), self.delta.get((s, "__ELSE__"), s))
        return s in self.accept

# Build DFAs
def build_hate_dfa() -> DFA:
    states = {"S", "SEEN"}
    alphabet = {"HATE", "OFFENSIVE", "LINK", "HASHTAG", "OTHER"}
    delta = {
        ("S", "HATE"): "SEEN",
        ("S", "__ELSE__"): "S",
        ("SEEN", "__ELSE__"): "SEEN",
    }
    return DFA(states, alphabet, "S", {"SEEN"}, delta)

def build_offensive_dfa() -> DFA:
    states = {"S", "SEEN"}
    alphabet = {"HATE", "OFFENSIVE", "LINK", "HASHTAG", "OTHER"}
    delta = {
        ("S", "OFFENSIVE"): "SEEN",
        ("S", "__ELSE__"): "S",
        ("SEEN", "__ELSE__"): "SEEN",
    }
    return DFA(states, alphabet, "S", {"SEEN"}, delta)

def build_spam_dfa() -> DFA:
    # states encode: L = link count (0,1,2+), H = hashtag count (0,1,2,3+)
    states = {
        "L0H0","L1H0","L2pH0",
        "L0H1","L1H1","L2pH1",
        "L0H2","L1H2","L2pH2",
        "L0H3p","L1H3p","L2pH3p"
    }
    accept = {"L2pH0","L2pH1","L2pH2","L2pH3p","L0H3p","L1H3p"}
    alphabet = {"LINK","HASHTAG","HATE","OFFENSIVE","OTHER"}
    delta = {}
    def step(s, sym):
        L = 2 if "L2p" in s else (1 if "L1" in s else 0)
        H = 3 if "H3p" in s else (2 if "H2" in s else (1 if "H1" in s else 0))
        if sym == "LINK": L = min(2, L+1)
        elif sym == "HASHTAG": H = min(3, H+1)
        # rebuild
        Ls = "L0" if L==0 else ("L1" if L==1 else "L2p")
        Hs = "H0" if H==0 else ("H1" if H==1 else ("H2" if H==2 else "H3p"))
        return f"{Ls}{Hs}"
    for s in list(states):
        for sym in alphabet:
            delta[(s, sym)] = step(s, sym)
        delta[(s, "__ELSE__")] = step(s, "OTHER")
    return DFA(states, alphabet, "L0H0", accept, delta)

# High-level classifier
from dataclasses import dataclass as _dc
@_dc
class ClassificationReport:
    hate: bool
    offensive: bool
    spam: bool
    details: dict

def classify(text: str) -> ClassificationReport:
    data = preprocess(text)
    tokens = data["tokens"]
    symbols = [categorize(t) for t in tokens]
    is_hate = build_hate_dfa().run(symbols)
    is_off = build_offensive_dfa().run(symbols)
    is_spam = build_spam_dfa().run(symbols)
    details = {
        "tokens": tokens,
        "symbols": symbols,
        "counts": {
            "links": sum(1 for s in symbols if s == "LINK"),
            "hashtags": sum(1 for s in symbols if s == "HASHTAG"),
        }
    }
    return ClassificationReport(is_hate, is_off, is_spam, details)

def _cli():
    import argparse
    p = argparse.ArgumentParser(description="DFA Content Classification")
    p.add_argument("post", type=str, help="Post text to classify (use quotes).")
    args = p.parse_args()
    print(json.dumps(classify(args.post).__dict__, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    _cli()
