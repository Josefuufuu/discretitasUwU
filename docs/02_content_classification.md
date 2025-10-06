# Content Classification (DFAs) — Step 2

We build **three DFAs** over a tiny alphabet:
`HATE`, `OFFENSIVE`, `LINK`, `HASHTAG`, `OTHER`.

- **Hate speech DFA** → accepts if a token is in `HATE_KEYWORDS`.
- **Offensive DFA** → accepts if a token is in `OFFENSIVE_KEYWORDS`.
- **Spam DFA** → accepts if there are **≥ 2 links** or **≥ 3 hashtags**.

Input tokens come from **post preprocessing** (your teammate's `regexRules.py`), which extracts mentions/hashtags/links/emojis and normalizes text. If that file is missing, the script uses a tiny local fallback.

## Run

```bash
python content_classification_dfa.py "go http://a.com http://b.com #wow"
```

Example output:

```json
{
  "hate": false,
  "offensive": false,
  "spam": true,
  "details": {
    "tokens": ["go", "http://a.com", "http://b.com", "#wow"],
    "symbols": ["OTHER", "LINK", "LINK", "HASHTAG"],
    "counts": {"links": 2, "hashtags": 1}
  }
}
```

## Edit keyword lists

Open `content_classification_dfa.py` and change:

```python
HATE_KEYWORDS = {"slur1", "slur2"}        # classroom placeholders
OFFENSIVE_KEYWORDS = {"stupid", "idiot"}  # simple examples
```

> For safety, keep neutral examples in class; real deployments load keywords from config files and apply context filters.

## Tests (pytest)

Create `tests/test_dfa.py`:

```python
from content_classification_dfa import classify

def test_spam_links():
    rep = classify("go http://a.com http://b.com")
    assert rep.spam is True

def test_spam_hashtags():
    rep = classify("#a #b #c hello")
    assert rep.spam is True

def test_offensive():
    rep = classify("you are stupid")
    assert rep.offensive is True

def test_hate_placeholder():
    rep = classify("slur1 is here")
    assert rep.hate is True
```

Run:
```bash
pip install pytest
pytest -q
```

## Theory link (short)

- DFA states represent *how much evidence we've seen* (e.g., 0/1/≥2 links).
- The alphabet is a small set of labels, so DFAs are clean and efficient.
- This step feeds the next module (FST) to mask or suggest actions.
