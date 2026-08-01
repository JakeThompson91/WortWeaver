import re
import io
import os
import logging
import functools
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify
import argostranslate.package
import argostranslate.translate
from pypdf import PdfReader

# Suppress HTTP access logging from Werkzeug and Waitress
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('waitress').setLevel(logging.ERROR)

app = Flask(__name__)

DEFAULT_FROM_CODE = "de"
TO_CODE = "en"

# Available supported source languages list for UI dropdown
SUPPORTED_LANGUAGES = [
    {"code": "de", "name": "German", "default": True},
    {"code": "fr", "name": "French"},
    {"code": "es", "name": "Spanish"},
    {"code": "it", "name": "Italian"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "nl", "name": "Dutch"},
    {"code": "ru", "name": "Russian"},
    {"code": "zh", "name": "Chinese"},
    {"code": "ja", "name": "Japanese"},
    {"code": "ko", "name": "Korean"},
    {"code": "pl", "name": "Polish"},
    {"code": "ar", "name": "Arabic"},
    {"code": "tr", "name": "Turkish"},
    {"code": "uk", "name": "Ukrainian"},
    {"code": "sv", "name": "Swedish"},
    {"code": "da", "name": "Danish"},
    {"code": "fi", "name": "Finnish"},
    {"code": "cs", "name": "Czech"},
    {"code": "hu", "name": "Hungarian"},
    {"code": "el", "name": "Greek"},
    {"code": "hi", "name": "Hindi"},
]

# Module-level pre-compiled regular expressions
PARAGRAPH_BOUNDARY_RE = re.compile(r'(?<=[.!?»”"])\n+(?=[\w0-9"»“])')
DOUBLE_NEWLINE_RE = re.compile(r'\n\s*\n')
SOFT_BREAK_RE = re.compile(r'(?<!\n)\n(?!\n)')
WHITESPACE_RE = re.compile(r'\s+')
SENTENCE_END_RE = re.compile(r'(?<=[.!?»”"])\s+')
CLEAN_WORD_RE = re.compile(r'^[^\w\s]+|[^\w\s]+$', re.UNICODE)

# Global cached translation model handles: (from_code, to_code) -> model
_TRANSLATION_MODELS = {}

def ensure_language_package(from_code: str, to_code: str = "en") -> bool:
    """Installs the requested ArgosTranslate language package if it is not installed yet."""
    try:
        installed = argostranslate.translate.get_installed_languages()
        installed_codes = [lang.code for lang in installed]
        
        if from_code not in installed_codes or to_code not in installed_codes:
            logging.info(f"Downloading translation package for {from_code} -> {to_code}...")
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            pkg = next(
                (p for p in available_packages if p.from_code == from_code and p.to_code == to_code),
                None
            )
            if pkg:
                download_path = pkg.download()
                argostranslate.package.install_from_path(download_path)
                logging.info(f"Successfully installed package for {from_code} -> {to_code}")
                return True
            else:
                logging.warning(f"Package for {from_code} -> {to_code} not found.")
                return False
        return True
    except Exception as e:
        logging.error(f"Error downloading package for {from_code} -> {to_code}: {e}")
        return False

def get_translation_model(from_code: str = "de", to_code: str = "en"):
    global _TRANSLATION_MODELS
    key = (from_code, to_code)
    if key not in _TRANSLATION_MODELS or _TRANSLATION_MODELS[key] is None:
        try:
            model = argostranslate.translate.get_translation_from_codes(from_code, to_code)
            if model is None:
                ensure_language_package(from_code, to_code)
                model = argostranslate.translate.get_translation_from_codes(from_code, to_code)
            _TRANSLATION_MODELS[key] = model
        except Exception as e:
            logging.error(f"Failed to get translation model for {from_code}->{to_code}: {e}")
            _TRANSLATION_MODELS[key] = None
    return _TRANSLATION_MODELS.get(key)

@functools.lru_cache(maxsize=8192)
def translate_text(text: str, from_code: str = "de", to_code: str = "en") -> str:
    """
    Cached translation wrapper bypassing package lookup overhead.
    Uses cached translation model handle and LRU cache for instant lookups.
    """
    if not text or not text.strip():
        return ""
    model = get_translation_model(from_code, to_code)
    if model:
        try:
            return model.translate(text)
        except Exception:
            pass
    try:
        return argostranslate.translate.translate(text, from_code, to_code)
    except Exception:
        return text

def setup_translation_model():
    """Initializes default ArgosTranslate package (German -> English) if needed and pre-warms translation model into RAM."""
    try:
        ensure_language_package(DEFAULT_FROM_CODE, TO_CODE)
        model = get_translation_model(DEFAULT_FROM_CODE, TO_CODE)
        if model:
            model.translate("Hallo")
    except Exception:
        pass

def split_into_paragraphs(text):
    """
    Splits raw text into distinct paragraphs based on line breaks, PDF page output, 
    and punctuation boundaries.
    """
    if not text:
        return []

    # Normalize carriage returns and line endings
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')

    # Convert single newlines following sentence terminators into double newlines
    normalized = PARAGRAPH_BOUNDARY_RE.sub('\n\n', normalized)

    # Split on double or multiple newlines
    raw_paragraphs = [p.strip() for p in DOUBLE_NEWLINE_RE.split(normalized) if p.strip()]

    clean_paragraphs = []
    for p in raw_paragraphs:
        # Replace soft single line breaks inside a paragraph with a single space
        single_line = SOFT_BREAK_RE.sub(' ', p)
        single_line = WHITESPACE_RE.sub(' ', single_line).strip()
        if single_line:
            clean_paragraphs.append(single_line)

    # Fallback for dense text/PDFs with no paragraph breaks: split every 3 sentences into a paragraph
    if len(clean_paragraphs) <= 1 and clean_paragraphs:
        full_text = clean_paragraphs[0]
        sentences = split_paragraph_into_sentences(full_text)
        if len(sentences) > 3:
            clean_paragraphs = []
            for i in range(0, len(sentences), 3):
                clean_paragraphs.append(" ".join(sentences[i:i+3]))

    return clean_paragraphs if clean_paragraphs else [text.strip()]

def split_paragraph_into_sentences(text):
    """
    Regex sentence boundary detection.
    Splits on sentence-ending punctuation (.!? or quote marks) followed by space/newline.
    """
    raw_sentences = SENTENCE_END_RE.split(text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    return sentences if sentences else [text.strip()]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/languages", methods=["GET"])
def get_languages():
    """Returns the list of supported source languages."""
    return jsonify({
        "languages": SUPPORTED_LANGUAGES,
        "default": DEFAULT_FROM_CODE
    })

@app.route("/spotcheck-process", methods=["POST"])
def spotcheck_process():
    """Processes input text into paragraph chunks and sentence pairs with parallel multi-threaded translation."""
    data = request.get_json() or {}
    source_text = data.get("text", "")
    from_code = data.get("from_code", DEFAULT_FROM_CODE)
    
    if not source_text.strip():
        return jsonify({"chunks": []})

    # Read customizable chunk_size (clamped between 1 and 10, defaulting to 3)
    try:
        chunk_size = int(data.get("chunk_size", 3))
        chunk_size = max(1, min(10, chunk_size))
    except (ValueError, TypeError):
        chunk_size = 3

    paragraphs = split_into_paragraphs(source_text)
    
    # Group paragraphs into customizable chunk sizes
    paragraph_groups = [paragraphs[i:i + chunk_size] for i in range(0, len(paragraphs), chunk_size)]
    
    # Extract sentence structure and collect unique sentences to translate
    chunk_sentence_map = []
    all_sentences = []
    
    for chunk_idx, p_group in enumerate(paragraph_groups):
        chunk_paragraphs = []
        for paragraph in p_group:
            sentences = split_paragraph_into_sentences(paragraph)
            cleaned_sentences = [s.strip() for s in sentences if s.strip()]
            chunk_paragraphs.append(cleaned_sentences)
            all_sentences.extend(cleaned_sentences)
        chunk_sentence_map.append(chunk_paragraphs)
    
    # Ensure model is ready and pre-warmed for selected source language
    get_translation_model(from_code, TO_CODE)
    
    # Multi-threaded concurrent sentence translation (CTranslate2 releases GIL)
    if all_sentences:
        unique_sentences = list(dict.fromkeys(all_sentences))
        max_workers = min(8, os.cpu_count() or 4)
        translate_func = functools.partial(translate_text, from_code=from_code, to_code=TO_CODE)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(translate_func, unique_sentences))

    # Construct final structured chunks from populated cache
    structured_chunks = []
    for chunk_idx, chunk_paragraphs in enumerate(chunk_sentence_map):
        chunk_data = {"chunk_id": chunk_idx + 1, "paragraphs": []}
        
        for sentences in chunk_paragraphs:
            p_data = []
            for s_clean in sentences:
                translated_s = translate_text(s_clean, from_code=from_code, to_code=TO_CODE)
                p_data.append({
                    "original": s_clean,
                    "translated": translated_s
                })
            if p_data:
                chunk_data["paragraphs"].append(p_data)
                
        structured_chunks.append(chunk_data)

    return jsonify({"chunks": structured_chunks})

@app.route("/translate-word", methods=["POST"])
def translate_word():
    """Translates an individual word or phrase on-demand for hover tooltips using LRU cache."""
    data = request.get_json() or {}
    raw_word = data.get("word", "").strip()
    from_code = data.get("from_code", DEFAULT_FROM_CODE)
    if not raw_word:
        return jsonify({"translation": ""})
    
    clean_word = CLEAN_WORD_RE.sub('', raw_word)
    target = clean_word if clean_word else raw_word
    
    translated = translate_text(target, from_code=from_code, to_code=TO_CODE)
        
    return jsonify({"original": raw_word, "clean": target, "translation": translated})

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    uploaded_file = request.files["file"]
    filename = uploaded_file.filename.lower()
    extracted_text = ""
    
    try:
        if filename.endswith(".txt"):
            extracted_text = uploaded_file.read().decode("utf-8", errors="ignore")
        elif filename.endswith(".pdf"):
            pdf_stream = io.BytesIO(uploaded_file.read())
            pdf_reader = PdfReader(pdf_stream)
            page_texts = []
            for page in pdf_reader.pages:
                try:
                    txt = page.extract_text()
                    if txt and txt.strip():
                        page_texts.append(txt.strip())
                except Exception:
                    continue
            extracted_text = "\n\n".join(page_texts)
        else:
            return jsonify({"error": "Please upload a .txt or .pdf file."}), 400

        return jsonify({"original_text": extracted_text})

    except Exception as e:
        return jsonify({"error": f"Failed to read file: {str(e)}"}), 500

if __name__ == "__main__":
    setup_translation_model()
    app.run(host="127.0.0.1", port=5000, debug=True)
