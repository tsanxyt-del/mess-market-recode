"""Ensure required MongoDB indexes exist (run after deploy / schema change)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402
django.setup()

from config.mongo import ensure_indexes  # noqa: E402

ensure_indexes()
print("Indexes ensured.")
