# Moderation Toolkit

This project provides a collection of finite-state and grammar-based utilities for
moderating short social media style posts. The toolkit can be used from the
command line for quick experiments or through a lightweight web dashboard for a
more visual workflow.

## Installation

```bash
python -m pip install -r requirements.txt
```

The dependencies include:

- [Flask](https://flask.palletsprojects.com/) for the optional web interface
- [textX](https://textx.github.io/textX/stable/) for context-free grammar parsing

## Command-line usage

Run the CLI helper to process a single post and view the aggregated JSON output:

```bash
python -m src.interface "Your post text goes here"
```

If the post text argument is omitted, the CLI prompts for interactive input.

## Web interface

The project also exposes a small Flask application that wraps the same
``process_post`` pipeline in an HTML form. Start the development server with one
of the following commands:

```bash
python -m src.web_interface
# or
flask --app src.web_interface run
```

Then open http://127.0.0.1:5000/ in your browser to access the moderation
dashboard. The page displays the original post, classification badge, masked
content and suggestions, validation status, and rendered preview.

## Running tests

```bash
pytest
```
