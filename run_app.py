"""
Cross-Platform Launcher for WörtWeaver
Automatically detects OS and uses Waitress WSGI server on Windows
or production, or Flask dev server.
"""

import logging
import sys

# Ensure UTF-8 stdout encoding on legacy Windows cp1252 consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Suppress HTTP access logging from WSGI and Flask servers
logging.getLogger("waitress").setLevel(logging.ERROR)
logging.getLogger("werkzeug").setLevel(logging.ERROR)


def main():
    print("========================================================")
    print("             WörtWeaver Translation Server              ")
    print("  -> Server Running at: http://127.0.0.1:5000           ")
    print("  (Press Ctrl+C to stop)                                ")
    print("========================================================")

    try:
        from waitress import serve

        from app import app, setup_translation_model

        setup_translation_model()
        serve(app, host="127.0.0.1", port=5000, threads=6, _quiet=True)
    except ImportError:
        from app import app, setup_translation_model

        setup_translation_model()
        app.run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
