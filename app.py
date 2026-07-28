import re
import io
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify
import argostranslate.package
import argostranslate.translate
from pypdf import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "wortweaver.log")

# Setup Rotating File Handler for wortweaver.log
try:
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=2, encoding="utf-8")
    file_formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
except Exception:
    file_handler = None

LOGGER_NAMES = ['werkzeug', 'waitress', 'app', 'gunicorn.error', 'gunicorn.access']
if file_handler:
    for name in LOGGER_NAMES:
        logger_obj = logging.getLogger(name)
        logger_obj.addHandler(file_handler)
        logger_obj.setLevel(logging.ERROR)

app = Flask(__name__)
if file_handler:
    app.logger.addHandler(file_handler)

FROM_CODE = "de"
TO_CODE = "en"

def setup_translation_model():
    try:
        installed = argostranslate.translate.get_installed_languages()
        installed_codes = [lang.code for lang in installed]
        
        if FROM_CODE not in installed_codes or TO_CODE not in installed_codes:
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            de_en_package = next(
                (pkg for pkg in available_packages if pkg.from_code == FROM_CODE and pkg.to_code == TO_CODE),
                None
            )
            if de_en_package:
                download_path = de_en_package.download()
                argostranslate.package.install_from_path(download_path)
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
    normalized = re.sub(r'(?<=[.!?»”"])\n+(?=[A-ZÄÖÜ0-9"»“])', '\n\n', normalized)

    # Split on double or multiple newlines
    raw_paragraphs = [p.strip() for p in re.split(r'\n\s*\n', normalized) if p.strip()]

    clean_paragraphs = []
    for p in raw_paragraphs:
        # Replace soft single line breaks inside a paragraph with a single space
        single_line = re.sub(r'(?<!\n)\n(?!\n)', ' ', p)
        single_line = re.sub(r'\s+', ' ', single_line).strip()
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
    Splits on sentence-ending punctuation (.!? or German quote marks) followed by space/newline.
    """
    # Regex matches sentence terminators (. ! ? » ") followed by whitespace or end-of-string
    sentence_end_pattern = r'(?<=[.!?»”"])\s+'
    raw_sentences = re.split(sentence_end_pattern, text)
    
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    return sentences if sentences else [text.strip()]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/spotcheck-process", methods=["POST"])
def spotcheck_process():
    """Processes input text into paragraph chunks and sentence pairs for interactive spot-checking."""
    data = request.get_json() or {}
    source_text = data.get("text", "")
    
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
    
    structured_chunks = []
    
    for chunk_idx, p_group in enumerate(paragraph_groups):
        chunk_data = {"chunk_id": chunk_idx + 1, "paragraphs": []}
        
        for paragraph in p_group:
            p_data = []
            # Split German paragraph into sentences
            sentences = split_paragraph_into_sentences(paragraph)
            
            for sentence in sentences:
                s_clean = sentence.strip()
                if s_clean:
                    translated_s = argostranslate.translate.translate(s_clean, FROM_CODE, TO_CODE)
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
    """Translates an individual word or phrase on-demand for hover tooltips."""
    data = request.get_json() or {}
    raw_word = data.get("word", "").strip()
    if not raw_word:
        return jsonify({"translation": ""})
    
    clean_word = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', raw_word, flags=re.UNICODE)
    target = clean_word if clean_word else raw_word
    
    try:
        translated = argostranslate.translate.translate(target, FROM_CODE, TO_CODE)
    except Exception as e:
        translated = target
        
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

is_file_logging_enabled = False

@app.route("/toggle-logging", methods=["POST"])
def toggle_logging():
    global is_file_logging_enabled
    try:
        data = request.get_json(silent=True) or {}
        enabled = data.get("enabled", not is_file_logging_enabled)
        is_file_logging_enabled = bool(enabled)
        
        target_level = logging.INFO if is_file_logging_enabled else logging.ERROR
        for name in LOGGER_NAMES:
            logging.getLogger(name).setLevel(target_level)
            
        status_text = "ENABLED" if is_file_logging_enabled else "DISABLED"
        logging.getLogger('app').info(f"File logging {status_text} -> outputting to {LOG_FILE}")
        
        return jsonify({
            "logging_enabled": is_file_logging_enabled,
            "log_file": LOG_FILE
        })
    except Exception as e:
        return jsonify({"error": str(e), "logging_enabled": is_file_logging_enabled}), 500

if __name__ == "__main__":
    setup_translation_model()
    app.run(host="127.0.0.1", port=5000, debug=True)
