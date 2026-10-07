"""Hindi display names for admin — Aloo (Potato) style.

Usage: {% load hindi %} ... {{ rec.item_name|hi }}
Falls back to the original text when no Hindi alias exists. Never raises.
"""
from django import template
from apps.items.constants import HINDI_ALIASES

register = template.Library()

_rev = None


def _index():
    global _rev
    if _rev is None:
        _rev = {}
        for eng, aliases in HINDI_ALIASES.items():
            _rev[eng.lower()] = eng
            for a in aliases or []:
                _rev.setdefault(str(a).lower(), eng)
    return _rev


@register.filter
def hi(name):
    try:
        key = str(name or "").strip()
        if not key:
            return ""
        eng = _index().get(key.lower())
        if not eng:
            return key
        aliases = HINDI_ALIASES.get(eng, []) or []
        hindi = next((a for a in aliases if str(a).lower() != eng.lower()), "")
        if hindi:
            return f"{hindi} ({eng})"
        return eng
    except Exception:
        return name
