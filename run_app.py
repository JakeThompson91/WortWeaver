"""
Cross-Platform Launcher for WortWeaver
Automatically detects OS and uses Waitress WSGI server on Windows / production, or Flask dev server.
"""

import sys
import os

def main():
    print("========================================================")
    print("             WortWeaver Translation Server              ")
    print("========================================================")
    
    try:
        from waitress import serve
        from app import app, setup_translation_model
        
        print("\n[1/2] Checking local German-English translation models...")
        setup_translation_model()
        
        print("\n[2/2] Serving WortWeaver via Waitress WSGI server...")
        print("👉 Open your web browser to: http://127.0.0.1:5000\n")
        serve(app, host="127.0.0.1", port=5000, threads=6)
    except ImportError:
        print("\n[Notice] Waitress not found, starting standard server...")
        from app import app, setup_translation_model
        setup_translation_model()
        app.run(host="127.0.0.1", port=5000)

if __name__ == "__main__":
    main()
