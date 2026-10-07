"""Storage abstraction — local MEDIA today, S3-compatible tomorrow.

To move to cloud storage later: implement the same three functions
(save_bill_file / delete_bill_file / bill_url) with boto3/django-storages
and swap the import — callers stay unchanged.
"""
import os
import uuid
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from .validators import validate_bill_file


def _bill_dir(purchase_date=None):
    dt = purchase_date
    if isinstance(purchase_date, str):
        try:
            dt = datetime.strptime(purchase_date, "%Y-%m-%d")
        except ValueError:
            dt = datetime.now()
    if not isinstance(dt, datetime):
        try:
            from datetime import date as _d
            if isinstance(dt, _d):
                dt = datetime(dt.year, dt.month, dt.day)
            else:
                dt = datetime.now()
        except Exception:
            dt = datetime.now()
    return f"bills/{dt.year}/{dt.month:02d}/{dt.day:02d}"


def save_bill_file(uploaded, purchase_date=None):
    """Validate + store. Returns MEDIA-relative path stored in MongoDB."""
    ext = validate_bill_file(uploaded)
    name = f"bill-{uuid.uuid4().hex[:10]}.{ext}"
    rel = f"{_bill_dir(purchase_date)}/{name}"
    return default_storage.save(rel, uploaded)


def delete_bill_file(rel_path):
    if rel_path and default_storage.exists(rel_path):
        default_storage.delete(rel_path)


def bill_url(rel_path):
    if not rel_path:
        return ""
    if rel_path.startswith("http"):
        return rel_path
    base = settings.MEDIA_URL.rstrip("/") + "/"
    return base + rel_path.lstrip("/")
