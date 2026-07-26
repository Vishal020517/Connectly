"""
Start the WhisperNet API server.
Run from the project root:  python -m backend.run
"""
import os
import uvicorn

# Ensure ChromaDB and relative paths resolve to project root
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_PROJECT_ROOT)

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
