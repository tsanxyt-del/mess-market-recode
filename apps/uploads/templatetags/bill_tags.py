"""Bill URL helpers — MEDIA or S3-proof, never breaks on absolute URLs."""
from django import template

register = template.Library()


@register.filter
def bill_url(rel_path):
    try:
        from apps.uploads.storage import bill_url as _bill_url
        return _bill_url(rel_path or "")
    except Exception:
        return ""


@register.filter
def is_pdf(rel_path):
    try:
        return str(rel_path or "").lower().endswith(".pdf")
    except Exception:
        return False
