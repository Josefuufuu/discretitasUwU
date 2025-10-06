"""Unified moderation interface for processing posts."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Any, Dict

from .moderation.content_classification_dfa import classify
from .moderation.content_transformation_fst import transform
from .moderation.post_validation_cfg import validate_post, render_preview


def process_post(post: str) -> Dict[str, Any]:
    """Run classification, transformation, and validation on ``post``.

    Parameters
    ----------
    post:
        Raw user supplied text.

    Returns
    -------
    Dict[str, Any]
        Aggregated results containing the original post, classification flag,
        transformation details, validation status, and rendered preview (when
        available).
    """

    classification_report = classify(post)
    classification_status = (
        "Violation"
        if any(
            (
                classification_report.hate,
                classification_report.offensive,
                classification_report.spam,
            )
        )
        else "Safe"
    )

    transformation_result = transform(post)

    is_valid, validation_obj = validate_post(post)
    if is_valid:
        preview = render_preview(validation_obj)
        validation_payload = {"status": "Valid", "error": None}
    else:
        preview = None
        validation_payload = {"status": "Invalid", "error": str(validation_obj)}

    return {
        "original_post": post,
        "classification": {
            "status": classification_status,
            "details": asdict(classification_report),
        },
        "transformation": asdict(transformation_result),
        "validation": validation_payload,
        "preview": preview,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Moderation interface")
    parser.add_argument(
        "post",
        nargs="?",
        help="Post text to process. If omitted, the program prompts for input.",
    )
    args = parser.parse_args()

    post = args.post
    if post is None:
        post = input("Enter the post to process: ")

    result = process_post(post)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
