# WörtWeaver - Interactive Granular Translation Spot-Checker

A modern, web-based tool for interactive, paragraph-by-paragraph spot-checking and editing of translations to English using local machine translation models (defaulting to German, with options for French, Spanish, Italian, and more).

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## ✨ Features

- 🔍 **Granular Spot-Checking Workspace**: Automatically segments documents into structured paragraph chunks for efficient review.
- 🌐 **Multi-Language Support**: Defaults to German ➔ English, while allowing users to select French, Spanish, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, and more.
- 🎨 **Distinct Editing Modes**:
  - **Sentence Mode** (`S` key / Warm Amber Theme): Click any translated sentence to edit its phrasing.
  - **Word Mode** (`W` key / Sky Blue Theme): Click individual target words to make pinpoint edits.
- 💡 **Instant Hover Word Translation** (`T` key / Vibrant Violet Theme):
  - Disabled by default for clean reading. Press **`T`** or click the header button to toggle ON/OFF.
  - Hover over any source word (or highlight text) to view instant local translations in an inline tooltip.
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

---

## 💻 Windows Setup & One-Click Launch

### Prerequisites (Installing Python via winget)
If Python is not yet installed on your Windows system, open **Command Prompt** or **PowerShell** and run:

```cmd
winget install -e --id Python.Python.3.13
```

*(Note: After installation finishes, close and reopen your terminal window so system PATH updates take effect).*

---

### Option A: One-Click Batch Script (Recommended for Windows)
1. Download or clone this repository to your computer.
2. Double-click **`run_windows.bat`**.
   *(This script automatically checks for Python, creates a virtual environment, installs all required packages, and launches the app via Waitress WSGI!)*
3. Open your web browser to **`http://127.0.0.1:5000`**.

### Option B: PowerShell Launcher
```powershell
.\run_windows.ps1
```

### Option C: Manual Command Prompt / Windows Setup
```cmd
:: 1. Create Virtual Environment
python -m venv venv

:: 2. Activate Virtual Environment
venv\Scripts\activate

:: 3. Install Dependencies (Includes Waitress for native Windows production WSGI)
pip install -r requirements.txt

:: 4. Launch WörtWeaver Server
python run_app.py
```

---

## 🐧 Linux / macOS Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/JakeThompson91/WortWeaver.git
cd WortWeaver

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Application
- **Standard Launcher (Waitress / Dev)**: `python run_app.py`
- **Linux Production (Gunicorn)**: `gunicorn -c gunicorn.conf.py wsgi:app`

Open your browser and navigate to **`http://127.0.0.1:5000`**.

---

## 🐳 Docker Setup

### Option 1: Docker Compose (Recommended)
```bash
# Build image and start WörtWeaver container in detached mode
docker compose up -d

# View server logs
docker compose logs -f

# Stop container
docker compose down
```

### Option 2: Docker CLI
```bash
# Build Docker image
docker build -t wortweaver:latest .

# Run container with persistent translation volume
docker run -d \
  --name wortweaver \
  -p 5000:5000 \
  -v wortweaver_argos_data:/home/appuser/.local/share/argos-translate \
  --restart unless-stopped \
  wortweaver:latest
```

Open your browser and navigate to **`http://localhost:5000`**.

---

## 🛠️ Project Structure

```
local-translation-app/
├── app.py                  # Flask backend & ArgoTranslate translation API endpoints
├── run_app.py              # Cross-platform launcher (Waitress / Flask)
├── run_windows.bat         # Windows one-click Command Prompt launcher
├── run_windows.ps1         # Windows PowerShell launcher
├── wsgi.py                 # Production WSGI application entrypoint
├── gunicorn.conf.py        # Production Gunicorn server configuration (Linux/macOS)
├── Dockerfile              # Production Docker container definition
├── docker-compose.yml      # Docker Compose service & volume config
├── .dockerignore           # Docker build exclusion patterns
├── static/
│   └── style.css           # Modular stylesheet and design system
├── templates/
│   └── index.html          # Web UI & interactive spot-check frontend logic
├── requirements.txt        # Cross-platform Python dependencies
├── .gitignore              # Git ignore configuration
├── LICENSE                 # MIT License
└── README.md               # Documentation
```
---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

