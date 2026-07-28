# WortWeaver - Interactive Granular Translation Spot-Checker

A modern, web-based tool for interactive, paragraph-by-paragraph spot-checking and editing of German to English translations using local machine translation models.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## ✨ Features

- 🔍 **Granular Spot-Checking Workspace**: Automatically segments documents into structured paragraph chunks for efficient review.
- 🎨 **Distinct Editing Modes**:
  - **Sentence Mode** (`S` key / Warm Amber Theme): Click any translated sentence to edit its phrasing.
  - **Word Mode** (`W` key / Sky Blue Theme): Click individual target words to make pinpoint edits.
- 💡 **Instant Hover Word Translation** (`T` key / Vibrant Violet Theme):
  - Disabled by default for clean reading. Press **`T`** or click the header button to toggle ON/OFF.
  - Hover over any German source word (or highlight text) to view instant local translations in an inline tooltip.
  - Quick `Google ↗` link in tooltips to open deep-linked searches on Google Translate.
- 📜 **Enhanced Dual Panel Navigation**: Scrollable containers with high-contrast custom scrollbars for navigating long texts.
- 📄 **Document Upload**: Supports uploading raw text (`.txt`) and PDF (`.pdf`) files.
- 💾 **Export**: Compile and download your spot-checked translation as a clean text file.
- 🔒 **Privacy-First & Local**: Powered by `argostranslate` for offline local machine translation.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
| :---: | :--- |
| **`S`** | Switch to **Sentence Mode** for whole-sentence editing |
| **`W`** | Switch to **Word Mode** for single-word replacement |
| **`T`** | Toggle **Hover Translation Mode** ON/OFF for source text |

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have Python 3.8 or higher installed on your system.

### 2. Clone Repository
```bash
git clone https://github.com/JakeThompson91/local-translation-app.git
cd local-translation-app
```

### 3. Create & Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to **`http://127.0.0.1:5000`**.

---

## 🛠️ Project Structure

```
local-translator/
├── app.py                  # Flask backend & ArgoTranslate translation API endpoints
├── templates/
│   └── index.html          # Web UI, CSS styles, interactive spot-check frontend logic
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore configuration
├── LICENSE                 # MIT License
└── README.md               # Documentation
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
