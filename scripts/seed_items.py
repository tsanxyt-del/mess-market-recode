"""Seed default item master into MongoDB."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402
django.setup()

from apps.items.services import seed_default_items  # noqa: E402

created = seed_default_items()
print(f"Seeded {created} new items (existing ones skipped).")
