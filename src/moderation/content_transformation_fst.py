
from __future__ import annotations
import re, json
from dataclasses import dataclass, asdict
from typing import List

try:
    from moderation.content_classification_dfa import classify, categorize, HATE_KEYWORDS, OFFENSIVE_KEYWORDS
    _HAVE_CLASSIFIER = True
except Exception:
    _HAVE_CLASSIFIER = False
    HATE_KEYWORDS = {"slur1", "slur2"}
    OFFENSIVE_KEYWORDS = {"stupid", "idiot"}
def categorize(token: str) -> str:
    if token.startswith("http") or token.startswith("www."):
        return "LINK"
    if token.startswith("#"):
        return "HASHTAG"
    core = re.sub(r"^[^\w]+|[^\w]+$", "", token.lower())
    if core in HATE_KEYWORDS:
        return "HATE"
    if core in OFFENSIVE_KEYWORDS:
        return "OFFENSIVE"
    return "OTHER"


@dataclass
class TransformResult:
    transformed_text: str
    masked_tokens: List[str]
    suggestions: List[str]
    categories: List[str]
    original_tokens: List[str]

def transform(post: str) -> TransformResult:
    if _HAVE_CLASSIFIER:
        rep = classify(post)
        raw_tokens = rep.details["tokens"]
        tokens = [t.lower() for t in raw_tokens]
        symbols = rep.details["symbols"]
        links = rep.details["counts"]["links"]
        hashtags = rep.details["counts"]["hashtags"]
        spam_detected = rep.spam
        hate_detected = rep.hate
        off_detected = rep.offensive
    else:
        norm = re.sub(r'\s+', ' ', post.lower()).strip()
        tokens = norm.split()
        raw_tokens = tokens
        symbols = [categorize(t) for t in tokens]
        links = sum(1 for s in symbols if s == "LINK")
        hashtags = sum(1 for s in symbols if s == "HASHTAG")
        spam_detected = (links >= 2) or (hashtags >= 3)
        hate_detected = any(s == "HATE" for s in symbols)
        off_detected = any(s == "OFFENSIVE" for s in symbols)

    out = []
    masked = []
    for tok, sym in zip(tokens, symbols):
        if sym in {"HATE", "OFFENSIVE"}:
            out.append("***")
            masked.append(tok.lower())
        else:
            out.append(tok)

    suggestions = []
    if hate_detected:
        suggestions.append("Warning: hate speech detected.")
    if off_detected:
        suggestions.append("Warning: offensive language detected.")
    if spam_detected:
        suggestions.append("Notice: looks like spam (too many links/hashtags).")

    return TransformResult(
        transformed_text=" ".join(out),
        masked_tokens=masked,
        suggestions=suggestions,
        categories=symbols,
        original_tokens=raw_tokens,
    )

def _cli():
    import argparse
    p = argparse.ArgumentParser(description="FST-based content transformation")
    p.add_argument("post", type=str)
    args = p.parse_args()
    print(json.dumps(asdict(transform(args.post)), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    _cli()
