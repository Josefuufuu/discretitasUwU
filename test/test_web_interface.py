import pytest

pytest.importorskip("textx")
pytest.importorskip("flask")

from src.web_interface import app


@pytest.fixture()
def client():
    app.config.update({"TESTING": True})
    with app.test_client() as client:
        yield client


def test_web_interface_displays_analysis(client):
    response = client.post("/", data={"post_text": "Hello idiot"})
    assert response.status_code == 200

    html = response.get_data(as_text=True)

    assert "Original Post" in html
    assert "Hello idiot" in html
    assert "Classification" in html
    assert "Violation" in html
    assert "Masked text:" in html
    assert "idiot" in html
    assert "Warning: offensive language detected." in html
    assert "Validation" in html
    assert "Valid" in html
    assert "Preview" in html
