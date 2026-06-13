import sys
import os

# Add project root to Python path so "backend.*" imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app — Vercel's Python runtime serves ASGI apps directly
from backend.main import app  # noqa: F401 — Vercel looks for `app`
