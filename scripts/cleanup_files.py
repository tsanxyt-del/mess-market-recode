"""Remove orphan bill files (on disk but not referenced in MongoDB)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django  # noqa: E402
django.setup()

from django.conf import settings
from apps.uploads.services import referenced_bill_paths  # noqa: E402

media_root = Path(settings.MEDIA_ROOT)
referenced = referenced_bill_paths()
removed = 0
for f in (media_root / "bills").rglob("*"):
    if f.is_file():
        rel = str(f.relative_to(media_root)).replace("\\", "/")
        if rel not in referenced:
            print(f"Orphan: {rel}")
            # f.unlink()  # uncomment to actually delete
            removed += 1
print(f"{removed} orphan file(s) found (dry run — uncomment unlink to delete).")
