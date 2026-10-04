import os
import sys
from pathlib import Path
import uvicorn

# Configure UTF-8 for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Add src to python path
src_dir = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_dir))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print("=======================================================")
    print(f"Starting Research Paper Analyzer Web App...")
    print(f"Access the application at: http://localhost:{port} (binding to {host}:{port})")
    print("=======================================================")

    uvicorn.run("server:app", host=host, port=port, reload=False)
