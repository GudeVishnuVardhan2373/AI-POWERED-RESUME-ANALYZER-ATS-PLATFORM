import sys
import os
import uvicorn


if __name__ == "__main__":
    # Ensure current directory is in PYTHONPATH
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Set utf-8 for Windows console
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 60)
    print("  [+] AI-POWERED RESUME ANALYZER & ATS PLATFORM")
    print("  Fullstack FastAPI + SQLAlchemy SQLite + Interactive UI")
    print("=" * 60)
    print("  Web Application:    http://127.0.0.1:8000")
    print("  API Docs (Swagger): http://127.0.0.1:8000/docs")
    print("  Database:           ai-resume-analyzer/database/resume_analyzer.db")
    print("=" * 60)
    print("  Press Ctrl+C to stop the server.\n")

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
