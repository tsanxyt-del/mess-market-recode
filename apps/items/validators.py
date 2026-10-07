"""Item validation."""
from apps.market.constants import UNIT_VALUES


class ItemValidationError(ValueError):
    pass


def validate_item_name(name):
    name = (name or "").strip()
    if not name:
        raise ItemValidationError("Item name is required.")
    if len(name) > 120:
        raise ItemValidationError("Item name is too long (max 120).")
    return name


def validate_default_unit(unit):
    u = (unit or "KG").strip().upper()
    if u not in UNIT_VALUES:
        raise ItemValidationError("Invalid unit.")
    return u


def validate_aliases(aliases):
    """Comma-string ya list → saaf alias list (max 10, har ek max 40 chars)."""
    if aliases is None:
        return []
    if isinstance(aliases, str):
        parts = [p.strip() for p in aliases.split(",")]
    else:
        parts = [str(p).strip() for p in aliases]
    out = []
    for p in parts:
        if p and len(p) <= 40 and p.lower() not in {a.lower() for a in out}:
            out.append(p)
    return out[:10]


def validate_category(category):
    from .constants import CATEGORIES
    c = (category or "").strip()
    if not c:
        return "Other"
    if len(c) > 40:
        raise ItemValidationError("Category is too long (max 40).")
    if c not in CATEGORIES:
        return "Other"
    return c
