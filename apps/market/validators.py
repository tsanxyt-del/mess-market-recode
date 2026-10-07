"""Backend validation — totals are always recomputed server-side."""
from datetime import datetime
from .constants import UNIT_VALUES


class MarketValidationError(ValueError):
    pass


def parse_purchase_date(value):
    from datetime import date as _date
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, _date):
        dt = datetime(value.year, value.month, value.day)
    elif isinstance(value, str):
        value = value.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                dt = datetime.strptime(value, fmt)
                break
            except ValueError:
                continue
        else:
            raise MarketValidationError("Invalid purchase date. Use YYYY-MM-DD.")
    else:
        raise MarketValidationError("Purchase date is required.")
    return datetime(dt.year, dt.month, dt.day)


def validate_quantity(value):
    try:
        q = float(value)
    except (TypeError, ValueError):
        raise MarketValidationError("Quantity must be a number.")
    if q <= 0:
        raise MarketValidationError("Quantity must be greater than 0.")
    if q > 100000:
        raise MarketValidationError("Quantity is unrealistically large.")
    return q


def validate_rate(value):
    try:
        r = float(value)
    except (TypeError, ValueError):
        raise MarketValidationError("Rate must be a number.")
    if r < 0:
        raise MarketValidationError("Rate cannot be negative.")
    if r > 10000000:
        raise MarketValidationError("Rate is unrealistically large.")
    return r


def validate_unit(value):
    v = (value or "").strip().upper()
    if v not in UNIT_VALUES:
        raise MarketValidationError(f"Invalid unit. Allowed: {', '.join(UNIT_VALUES)}")
    return v


def compute_total(quantity, rate):
    """Single source of truth for totals (frontend mirrors this only for UX)."""
    return round(float(quantity) * float(rate), 2)


def validate_record_payload(item_id, item_name, quantity, unit, rate, purchase_date):
    if not item_name or not str(item_name).strip():
        raise MarketValidationError("Item is required.")
    q = validate_quantity(quantity)
    r = validate_rate(rate)
    u = validate_unit(unit)
    dt = parse_purchase_date(purchase_date)
    total = compute_total(q, r)
    return {
        "item_id": (item_id or "").strip(),
        "item_name": str(item_name).strip(),
        "quantity": q,
        "unit": u,
        "rate": r,
        "total": total,
        "purchase_date": dt,
        "year": dt.year,
        "month": dt.month,
    }
