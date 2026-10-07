"""Quick MongoDB connectivity check. Run: python scripts/check_mongo.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402
django.setup()

from django.conf import settings  # noqa: E402
from config.mongo import ping  # noqa: E402

print(f"URI: {settings.MONGODB_URI}")
print(f"DB : {settings.MONGODB_DATABASE}")
if ping():
    print("OK: MongoDB connected.")
else:
    print("DOWN: MongoDB se connect nahi ho pa raha.")
    print("Fix: Admin PowerShell me chalao -> winget install -e --id MongoDB.Server")
    print("Phir: net start MongoDB")
