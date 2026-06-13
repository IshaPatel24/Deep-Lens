"""
Entry point for Vercel web service deployment.
When Vercel deploys the backend service with `"root": "backend"`,
the working directory is `backend/`. We must add the parent directory
to sys.path so that `from backend.X import Y` imports resolve correctly.
"""
import sys
import os

# Add project root (parent of backend/) to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Re-export the FastAPI app — Vercel / uvicorn binds to `run:app`
from backend.main import app  # noqa: F401
