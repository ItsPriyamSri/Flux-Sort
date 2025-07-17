#!/usr/bin/env python3
"""
FluxSort v2 — Web UI server entry point.
Starts the FastAPI server and opens the browser automatically.
"""

import sys
import threading
import time
import webbrowser
from pathlib import Path

# Ensure src is importable when run directly
sys.path.insert(0, str(Path(__file__).parent))

HOST = "127.0.0.1"
PORT = 8765
URL = f"http://{HOST}:{PORT}"


def _open_browser() -> None:
    """Open the browser after a short delay to let the server boot."""
    time.sleep(1.5)
    webbrowser.open(URL)


def main() -> None:
    """Start the FluxSort web UI server."""
    try:
        import uvicorn
    except ImportError:
        print("ERROR: uvicorn not found. Run: pip install fluxsort")
        sys.exit(1)

    from src.api.server import app

    print("━" * 50)
    print("  🌊 FluxSort v2")
    print(f"  ✦  Server: {URL}")
    print("  ✦  Press Ctrl+C to stop")
    print("━" * 50)

    opener = threading.Thread(target=_open_browser, daemon=True)
    opener.start()

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
