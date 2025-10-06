import pytest

pytest.importorskip("textx")
from textx import TextXSyntaxError

from src.moderation.post_validation_cfg import (
    validate_post,
    render_preview,
    _flip_map,
)


def test_validate_post_success_and_rendering():
    txt = "Hi -italic- *bold* _under_ $a^2+b^2=c^2$ @alice #math https://test.com"
    ok, model = validate_post(txt)
    assert ok is True

    preview = render_preview(model)

    assert "*italic*" in preview
    assert "**bold**" in preview
    assert "<u>under</u>" in preview
    assert "$ a^2+b^2=c^2 $" in preview
    assert "@alice" in preview
    assert "**Hashtags:** #math" in preview
    assert "**Links:** https://test.com" in preview


def test_validate_post_invalid_hashtag():
    txt = "Hello #not-valid"
    ok, error = validate_post(txt)

    assert ok is False
    assert isinstance(error, TextXSyntaxError)


def test_render_preview_upside_down():
    txt = "~Hello123~"
    ok, model = validate_post(txt)
    assert ok is True

    preview = render_preview(model)

    expected = "Hello123".translate(_flip_map)[::-1]
    assert expected in preview
