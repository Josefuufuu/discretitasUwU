import pytest
from src.moderation.content_transformation_fst import transform

# Helper for quick call
def _t(text):
    return transform(text)

# 1) Offensive language masking
@pytest.mark.parametrize("post", [
    "you are stupid",
    "IDIOT! stop that",
    "oye bro, you are Idiot!"
])
def test_masks_offensive_words(post):
    r = _t(post)
    assert "***" in r.transformed_text
    assert any("offensive" in s.lower() for s in r.suggestions)
    # original offensive word should appear in masked_tokens
    assert any("idiot" in m or "stupid" in m for m in r.masked_tokens)

# 2) Hate speech placeholders 
def test_masks_hate_word():
    r = _t("this contains slur1 example")
    assert "***" in r.transformed_text
    assert any("hate" in s.lower() for s in r.suggestions)

# 3) Spam detection
def test_spam_two_links():
    r = _t("go http://a.com http://b.com #wow")
    assert any("spam" in s.lower() for s in r.suggestions)

def test_spam_three_hashtags():
    r = _t("#a #b #c hello")
    assert any("spam" in s.lower() for s in r.suggestions)

def test_not_spam_one_link_two_hashtags():
    r = _t("visit http://a.com #a #b ok")
    assert not any("spam" in s.lower() for s in r.suggestions)

# 4) Clean posts 
def test_clean_post():
    r = _t("just a friendly hello world")
    assert r.suggestions == []
    assert "***" not in r.transformed_text

# 5) Mixed-language with emoji
def test_mixed_language_with_emoji():
    r = _t("oye bro, you are stupid 😄 #test")
    assert "***" in r.transformed_text
    assert any("offensive" in s.lower() for s in r.suggestions)
