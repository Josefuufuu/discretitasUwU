
import pytest
from moderation.content_classification_dfa import classify

@pytest.fixture(autouse=True)
def fixed_keywords(monkeypatch):
    monkeypatch.setattr("moderation.content_classification_dfa.HATE_KEYWORDS", {"slur1", "slur2"}, raising=False)
    monkeypatch.setattr("moderation.content_classification_dfa.OFFENSIVE_KEYWORDS", {"stupid", "idiot"}, raising=False)

# Offensive language
@pytest.mark.parametrize("post", [
    "you are stupid",
    "IDIOT! stop that",
    "He said: sTuPiD idea"
])
def test_offensive_language(post):
    rep = classify(post)
    assert rep.offensive is True
    assert rep.hate is False
    assert rep.spam is False

# Multiple hashtags/links (spam)
def test_spam_two_links():
    rep = classify("go http://a.com http://b.com #wow")
    assert rep.spam is True

def test_spam_three_hashtags():
    rep = classify("#a #b #c hello")
    assert rep.spam is True

def test_not_spam_one_link_two_hashtags():
    rep = classify("visit http://a.com #a #b ok")
    assert rep.spam is False

# Mixed-language
@pytest.mark.parametrize("post, expect_offensive", [
    ("oye bro, eso fue muy tonto 😄", False),
    ("hey bro, you are an idiot 😄", True),
])
def test_mixed_language(post, expect_offensive):
    rep = classify(post)
    rep2 = classify(post.upper())
    assert rep.offensive is expect_offensive
    assert rep.offensive == rep2.offensive

# Edge cases
def test_empty():
    rep = classify("   ")
    assert (rep.hate, rep.offensive, rep.spam) == (False, False, False)
