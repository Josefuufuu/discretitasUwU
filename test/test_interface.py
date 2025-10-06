import pytest

pytest.importorskip("textx")

from src.interface import process_post


def test_process_post_aggregates_outputs():
    post = "Hello world"

    result = process_post(post)

    assert result["original_post"] == post
    assert result["classification"]["status"] == "Safe"
    classification_details = result["classification"]["details"]
    assert classification_details["hate"] is False
    assert classification_details["offensive"] is False
    assert classification_details["spam"] is False

    transformation = result["transformation"]
    assert transformation["transformed_text"] == "hello world"
    assert transformation["masked_tokens"] == []
    assert transformation["suggestions"] == []

    validation = result["validation"]
    assert validation["status"] == "Valid"
    assert validation["error"] is None

    preview = result["preview"]
    assert isinstance(preview, str)
    assert "Hello" in preview
