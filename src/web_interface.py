"""Web interface for the moderation toolkit."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask, render_template, request

from src.interface import process_post

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

app = Flask(__name__, template_folder=str(TEMPLATE_DIR))


def _build_context(post_text: str, result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return {"post_text": post_text, "result": result}


@app.route("/", methods=["GET", "POST"])
def moderation_dashboard():
    post_text = ""
    result: Optional[Dict[str, Any]] = None

    if request.method == "POST":
        post_text = request.form.get("post_text", "")
        result = process_post(post_text)

    return render_template("moderation.html", **_build_context(post_text, result))


def run() -> None:
    """Run the Flask development server."""

    app.run(debug=False)


if __name__ == "__main__":
    run()
