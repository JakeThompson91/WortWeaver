import io

import pytest

from app import app, split_into_paragraphs, split_paragraph_into_sentences


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# --- 1. Text Processing & Segmentation Unit Tests ---


def test_split_into_paragraphs_empty():
    assert split_into_paragraphs("") == []
    assert split_into_paragraphs(None) == []


def test_split_into_paragraphs_normal():
    raw_text = "Erster Absatz.\n\nZweiter Absatz.\n\nDritter Absatz."
    paragraphs = split_into_paragraphs(raw_text)
    assert len(paragraphs) == 3
    assert paragraphs[0] == "Erster Absatz."
    assert paragraphs[1] == "Zweiter Absatz."
    assert paragraphs[2] == "Dritter Absatz."


def test_split_into_paragraphs_soft_breaks():
    raw_text = "Dies ist eine Zeile ohne Punkt\nim selben Absatz."
    paragraphs = split_into_paragraphs(raw_text)
    assert len(paragraphs) == 1
    assert "Dies ist eine Zeile ohne Punkt im selben Absatz." in paragraphs[0]


def test_split_into_paragraphs_punctuation_newline():
    raw_text = "Dies ist eine Zeile mit Punkt.\nDies ist die zweite Zeile."
    paragraphs = split_into_paragraphs(raw_text)
    assert len(paragraphs) == 2
    assert paragraphs[0] == "Dies ist eine Zeile mit Punkt."
    assert paragraphs[1] == "Dies ist die zweite Zeile."


def test_split_paragraph_into_sentences():
    text = "Hallo Welt! Wie geht es dir? Das ist ein Test."
    sentences = split_paragraph_into_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "Hallo Welt!"
    assert sentences[1] == "Wie geht es dir?"
    assert sentences[2] == "Das ist ein Test."


# --- 2. Flask Route Integration Tests ---


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert (
        b"W\xc3\xb6rtWeaver" in response.data
        or b"WortWeaver" in response.data
        or b"Spot-Check" in response.data
    )


def test_get_languages(client):
    response = client.get("/languages")
    assert response.status_code == 200
    data = response.get_json()
    assert "languages" in data
    assert "default" in data
    assert data["default"] == "de"
    assert any(lang["code"] == "de" for lang in data["languages"])


def test_get_installed_languages(client):
    response = client.get("/installed-languages")
    assert response.status_code == 200
    data = response.get_json()
    assert "packages" in data
    assert "installed_codes" in data


def test_upload_file_txt(client):
    data = {
        "file": (
            io.BytesIO(b"Guten Tag Welt!\n\nDies ist eine Testdatei."),
            "sample.txt",
        )
    }
    response = client.post(
        "/upload", data=data, content_type="multipart/form-data"
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert "original_text" in json_data
    assert "Guten Tag Welt!" in json_data["original_text"]


def test_upload_file_missing(client):
    response = client.post("/upload", data={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_upload_file_invalid_extension(client):
    data = {"file": (io.BytesIO(b"binary data"), "image.png")}
    response = client.post(
        "/upload", data=data, content_type="multipart/form-data"
    )
    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_spotcheck_process_empty(client):
    response = client.post("/spotcheck-process", json={"text": ""})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["chunks"] == []


def test_spotcheck_process_valid(client):
    payload = {
        "text": "Hallo Welt. Das ist ein fantastischer Tag.",
        "chunk_size": 2,
        "from_code": "de",
    }
    response = client.post("/spotcheck-process", json=payload)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "chunks" in json_data
    assert len(json_data["chunks"]) > 0
    first_chunk = json_data["chunks"][0]
    assert "chunk_id" in first_chunk
    assert "paragraphs" in first_chunk
    assert len(first_chunk["paragraphs"]) > 0


def test_translate_word(client):
    payload = {"word": "Hallo,", "from_code": "de"}
    response = client.post("/translate-word", json=payload)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["original"] == "Hallo,"
    assert json_data["clean"] == "Hallo"
    assert "translation" in json_data


def test_install_language_missing_code(client):
    response = client.post("/install-language", json={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False


def test_uninstall_languages_missing_codes(client):
    response = client.post("/uninstall-languages", json={"codes": []})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
