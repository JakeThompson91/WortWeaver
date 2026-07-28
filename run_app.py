"""
Cross-Platform Launcher for WortWeaver
Automatically detects OS and uses Waitress WSGI server on Windows / production, or Flask dev server.
"""

import logging

# Suppress HTTP access logging from WSGI and Flask servers
logging.getLogger('waitress').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

def main():
    print("========================================================")
    print("             WortWeaver Translation Server              ")
    print("  👉 Server Running at: http://127.0.0.1:5000           ")
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
