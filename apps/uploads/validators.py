"""Bill file validation (type + size). Never store files inside MongoDB."""
import os
from django.conf import settings


class UploadValidationError(ValueError):
    pass


def validate_bill_file(uploaded):
    if not uploaded:
        raise UploadValidationError("No file provided.")
    if not getattr(uploaded, "size", 1):
        raise UploadValidationError("Empty file is not allowed.")
    ext = os.path.splitext(uploaded.name)[1].lower().lstrip(".")
    if ext not in settings.ALLOWED_BILL_EXTENSIONS:
        raise UploadValidationError(
            f"Invalid file type '.{ext}'. Allowed: {', '.join(settings.ALLOWED_BILL_EXTENSIONS)}")
    if uploaded.size > settings.MAX_UPLOAD_SIZE:
        mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise UploadValidationError(f"File too large. Max {mb:.1f} MB.")
    # Basic content-type sanity check (allow only configured types)
    ctype = getattr(uploaded, "content_type", "") or ""
    ok_types = ("image/jpeg", "image/png", "image/webp", "application/pdf")
    if ctype and ctype not in ok_types:
        raise UploadValidationError(f"Unsupported content type: {ctype}")
    return ext
