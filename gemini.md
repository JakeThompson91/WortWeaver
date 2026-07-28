# Local Translator - Project Context & Developer Guidelines

## 📌 Project Overview
**Local Translator** is a lightweight, privacy-first web application for interactive German-to-English translation spot-checking. It allows translators to review and refine machine-translated text paragraph-by-paragraph with granular editing controls and instant dictionary hover lookups.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, Flask framework
- **Translation Engine**: `argostranslate` (Open-source offline neural machine translation)
- **Document Parsing**: `pypdf` (PDF extraction), built-in UTF-8 plain text parsing
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+) — *No external frontend frameworks or heavy dependencies required*.

---

## 🏗️ Architecture & Key Components

### 1. Backend (`app.py`)
- **`GET /`**: Renders main workspace (`templates/index.html`).
- **`POST /spotcheck-process`**:
  - Normalizes line breaks and splits raw German text into paragraphs.
  - Chunks paragraphs into groups of 3 paragraphs each.
  - Performs regex sentence boundary detection (`split_paragraph_into_sentences`).
  - Translates German sentences to English via `argostranslate`.
  - Returns structured JSON payload of chunks, paragraphs, and sentence pairs.
- **`POST /translate-word`**:
  - Receives an individual word or short phrase.
  - Cleans surrounding punctuation marks.
  - Translates the word on-demand via `argostranslate` for hover tooltips.
- **`POST /upload`**:
  - Handles `.txt` and `.pdf` file uploads and extracts raw text.

### 2. Frontend (`templates/index.html`)
- **State Management**: Manages active chunk index, approval states (`approvalState`), current selection mode (`sentence` vs `word`), and hover translation state (`isTranslateHoverEnabled`).
- **Interactive Editing**:
  - **Sentence Mode** (`S` key): Renders whole translated sentences as clickable units. Clicking opens an inline text input to edit phrasing.
  - **Word Mode** (`W` key): Splits target sentences into individual tokens. Clicking a word opens an input box to update specific words.
- **Hover Translation & Dictionary** (`T` key):
  - When enabled (`isTranslateHoverEnabled = true`), hovering over any German word in the Original panel fetches or uses cached word translations (`wordTranslationCache`).
  - Displays a floating popover above the word with the translation and a `Google ↗` deep link.
- **UI Design System**:
  - **Page Background**: Modern blue gradient (`linear-gradient(135deg, #e0f2fe 0%, #dbeafe 50%, #eff6ff 100%)`).
  - **Sentence Mode Button**: Warm Amber theme (`#d97706` active, `#fef3c7` inactive).
  - **Word Mode Button**: Sky Blue theme (`#0284c7` active, `#e0f2fe` inactive).
  - **Translate Hover Button**: Vibrant Purple theme (`#7c3aed` active, `#ede9fe` inactive).
  - **Scrollbars**: Forced visible custom scrollbars (`::-webkit-scrollbar` & `scrollbar-width`) on workspace panels (`.chunk-viewer`).

---

## ⌨️ Global Keyboard Shortcuts

- **`S`**: Switch to **Sentence Mode**
- **`W`**: Switch to **Word Mode**
- **`T`**: Toggle **Hover Word Translation** ON / OFF

*Note: Shortcuts are automatically bypassed when focused inside editable text areas or input elements.*

---

## 🚀 Development Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start development server
python app.py
```

---

## ⚙️ Development Guidelines for AI & Developers

1. **Maintain Pure Vanilla Web Tech**: Keep UI logic lightweight in vanilla CSS and JavaScript inside `templates/index.html`.
2. **Preserve Offline Privacy**: All core translations must use `argostranslate` locally.
3. **Keyboard Shortcut Safety**: When adding new shortcuts, ensure `document.activeElement` checks remain intact so keypresses in text inputs are not intercepted.
4. **Cache Efficiencies**: Frontend word translations should leverage `wordTranslationCache` to avoid duplicate backend requests for repeated vocabulary.
