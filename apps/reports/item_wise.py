"""Item-wise report: all purchases of one item (+ optional month filter)."""
import re
from datetime import datetime
from config.mongo import get_collection
from apps.market.selectors import _base_match, serialize


def item_wise_report(item_name, year=None, month=None):
    item_name = (item_name or "").strip()
    if not item_name:
        return {"item": "", "rows": [], "total_quantity": 0,
                "total_amount": 0, "purchases": 0, "unit": ""}
    match = _base_match({"item_name": {"$regex": f"^{re.escape(item_name)}$", "$options": "i"}})
    if year:
        match["year"] = int(year)
    if month:
        match["month"] = int(month)
    col = get_collection("market_records")
    docs = list(col.find(match).sort("purchase_date", 1))
    items = [serialize(d) for d in docs]
    return {
        "item": item_name,
        "rows": [{
            "date": r.get("purchase_date"), "display": r.get("purchase_date_display"),
            "quantity": r.get("quantity"), "unit": r.get("unit"),
            "rate": r.get("rate"), "total": r.get("total"),
        } for r in items],
        "total_quantity": round(sum(float(r.get("quantity", 0)) for r in items), 2),
        "total_amount": round(sum(float(r.get("total", 0)) for r in items), 2),
        "purchases": len(items),
        "unit": items[0].get("unit") if items else "",
    }
