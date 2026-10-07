"""Pure calculation helpers (also mirrored in static/js for instant UX)."""


def calc_total(quantity, rate):
    return round(float(quantity or 0) * float(rate or 0), 2)


def summarize(records):
    total_amount = round(sum(float(r.get("total", 0)) for r in records), 2)
    return {
        "count": len(records),
        "total_amount": total_amount,
        "total_quantity": round(sum(float(r.get("quantity", 0)) for r in records), 2),
    }


def inr(value):
    try:
        return f"₹{float(value):,.2f}".rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        return "₹0"
