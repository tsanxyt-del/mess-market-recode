"""Backup MongoDB (mongodump) + media folder. Run: python scripts/backup_database.py"""
import os
from dotenv import load_dotenv
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")
BACKUP_DIR = BASE / "backups" / datetime.now().strftime("%Y%m%d-%H%M%S")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGODB_DATABASE", "mess_market_db")

print(f"Backing up to {BACKUP_DIR}")
# 1. MongoDB dump (requires mongodump on PATH)
try:
    subprocess.run(["mongodump", f"--uri={MONGO_URI}", f"--db={MONGO_DB}",
                    f"--out={BACKUP_DIR / 'mongo'}"],
                   check=True)
    print("MongoDB dump OK.")
except FileNotFoundError:
    print("WARNING: `mongodump` not found — skipping DB dump. See docs/BACKUP.md.")
except subprocess.CalledProcessError as e:
    print(f"mongodump failed: {e}")

# 2. Media files
media = BASE / "media"
if media.exists():
    shutil.make_archive(str(BACKUP_DIR / "media"), "zip", media)
    print("Media backup OK.")
print("Done.")
