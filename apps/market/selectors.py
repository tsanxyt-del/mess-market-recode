"""Read queries (selectors) — MongoDB aggregation, never full-table in JS."""
import re
from datetime import datetime, timezone
from bson import ObjectId
from config.mongo import get_collection


def _base_match(extra=None):
    m = {"$or": [{"deleted_at": None}, {"deleted_at": {"$exists": False}}]}
    if extra:
        m.update(extra)
    return m


def serialize(doc):
    if not doc:
        return None
    d = dict(doc)
    d["id"] = str(d.pop("_id"))
    pd = d.get("purchase_date")
    if isinstance(pd, datetime):
        d["purchase_date"] = pd.strftime("%Y-%m-%d")
        d["purchase_date_display"] = pd.strftime("%d %b %Y")
    for k in ("created_at", "updated_at", "deleted_at"):
        v = d.get(k)
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


def get_record(record_id):
    try:
        oid = ObjectId(record_id)
    except Exception:
        return None
    return serialize(get_collection("market_records").find_one({"_id": oid, **_base_match()}))


def _match_from_filters(filters):
    """Shared Mongo match builder (list + summary dono use karte hain)."""
    filters = filters or {}
    match = _base_match()
    if filters.get("year"):
        match["year"] = int(filters["year"])
    if filters.get("month"):
        match["month"] = int(filters["month"])
    if filters.get("item"):
        match["item_name"] = {"$regex": re.escape(filters["item"]), "$options": "i"}
    if filters.get("unit"):
        match["unit"] = filters["unit"]
    if filters.get("date"):
        try:
            dt = datetime.strptime(filters["date"], "%Y-%m-%d")
            match["purchase_date"] = datetime(dt.year, dt.month, dt.day)
        except ValueError:
            pass
    if filters.get("date_from") or filters.get("date_to"):
        rng = {}
        try:
            if filters.get("date_from"):
                d = datetime.strptime(filters["date_from"], "%Y-%m-%d")
                rng["$gte"] = datetime(d.year, d.month, d.day)
            if filters.get("date_to"):
                d = datetime.strptime(filters["date_to"], "%Y-%m-%d")
                rng["$lte"] = datetime(d.year, d.month, d.day, 23, 59, 59)
            if rng:
                match["purchase_date"] = rng
        except ValueError:
            pass
    if filters.get("min_amount") not in (None, ""):
        match.setdefault("total", {})["$gte"] = float(filters["min_amount"])
    if filters.get("max_amount") not in (None, ""):
        match.setdefault("total", {})["$lte"] = float(filters["max_amount"])
    if filters.get("q"):
        q = filters["q"]
        match["$and"] = match.get("$and", []) + [{
            "$or": [
                {"item_name": {"$regex": re.escape(q), "$options": "i"}},
                {"remark": {"$regex": re.escape(q), "$options": "i"}},
            ]
        }]
    return match


def records_summary(filters=None):
    """Filter ke hisab se kul jod: amount + entries + din (pagination se alag)."""
    col = get_collection("market_records")
    match = _match_from_filters(filters)
    rows = list(col.aggregate([
        {"$match": match},
        {"$group": {"_id": "$purchase_date",
                    "amount": {"$sum": "$total"},
                    "count": {"$sum": 1}}},
    ]))
    return {
        "total_amount": round(sum(r.get("amount", 0) for r in rows), 2),
        "total_count": sum(r.get("count", 0) for r in rows),
        "days_count": len(rows),
    }


def list_records(filters=None, page=1, page_size=20, sort="-purchase_date"):
    """Server-side filter + sort + paginate."""
    filters = filters or {}
    match = _match_from_filters(filters)

    sort_field = (sort or "-purchase_date").lstrip("+-")
    sort_dir = -1 if str(sort).startswith("-") else 1
    allowed = {"purchase_date", "total", "item_name", "quantity", "rate", "created_at"}
    if sort_field not in allowed:
        sort_field, sort_dir = "purchase_date", -1

    col = get_collection("market_records")
    total_count = col.count_documents(match)
    try:
        page = max(1, int(page))
        page_size = min(100, max(1, int(page_size)))
    except (TypeError, ValueError):
        page, page_size = 1, 20
    cursor = (col.find(match).sort(sort_field, sort_dir)
              .skip((page - 1) * page_size).limit(page_size))
    items = [serialize(d) for d in cursor]
    pages = max(1, -(-total_count // page_size))
    return {"items": items, "total": total_count, "page": page,
            "page_size": page_size, "pages": pages}


def month_summary(year, month):
    """All monthly KPIs computed via aggregation (never hard-coded)."""
    col = get_collection("market_records")
    match = _base_match({"year": int(year), "month": int(month)})
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": None,
            "total_amount": {"$sum": "$total"},
            "total_items": {"$sum": 1},
            "total_quantity": {"$sum": "$quantity"},
        }},
    ]
    agg = list(col.aggregate(pipeline))
    base = {"total_amount": 0, "total_items": 0, "total_quantity": 0}
    if agg:
        base = {"total_amount": round(agg[0].get("total_amount", 0), 2),
                "total_items": agg[0].get("total_items", 0),
                "total_quantity": round(agg[0].get("total_quantity", 0), 2)}
    # date-wise breakdown
    days = list(col.aggregate([
        {"$match": match},
        {"$group": {"_id": "$purchase_date", "items": {"$sum": 1}, "amount": {"$sum": "$total"}}},
        {"$sort": {"_id": 1}},
    ]))
    day_list = []
    for d in days:
        pd = d["_id"]
        day_list.append({
            "date": pd.strftime("%Y-%m-%d") if isinstance(pd, datetime) else str(pd),
            "display": pd.strftime("%d %B %Y") if isinstance(pd, datetime) else str(pd),
            "items": d["items"],
            "amount": round(d["amount"], 2),
        })
    recorded_days = len(day_list)
    amounts = [d["amount"] for d in day_list]
    base.update({
        "recorded_days": recorded_days,
        "days": day_list,
        "avg_daily": round(base["total_amount"] / recorded_days, 2) if recorded_days else 0,
        "highest_day": max(day_list, key=lambda x: x["amount"]) if day_list else None,
        "lowest_day": min(day_list, key=lambda x: x["amount"]) if day_list else None,
    })
    return base


def day_records(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return {"date": date_str, "display": date_str, "items": [],
                "total_amount": 0, "total_items": 0, "total_quantity": 0}
    col = get_collection("market_records")
    docs = list(col.find(_base_match({"purchase_date": datetime(dt.year, dt.month, dt.day)}))
                 .sort("created_at", 1))
    items = [serialize(d) for d in docs]
    return {"date": date_str,
            "display": dt.strftime("%d %B %Y"),
            "items": items,
            "total_items": len(items),
            "total_amount": round(sum(float(i.get("total", 0)) for i in items), 2),
            "total_quantity": round(sum(float(i.get("quantity", 0)) for i in items), 2)}


def available_months():
    col = get_collection("market_records")
    rows = list(col.aggregate([
        {"$match": _base_match()},
        {"$group": {"_id": {"year": "$year", "month": "$month"},
                    "items": {"$sum": 1}, "amount": {"$sum": "$total"}}},
        {"$sort": {"_id.year": -1, "_id.month": -1}},
    ]))
    out = []
    for r in rows:
        y, m = r["_id"]["year"], r["_id"]["month"]
        out.append({"year": y, "month": m, "items": r["items"],
                    "amount": round(r["amount"], 2)})
    return out


def available_years():
    return sorted({m["year"] for m in available_months()}, reverse=True)


def search_public(query, year=None, month=None, limit=50):
    match = _base_match()
    if query:
        rx = {"$regex": re.escape(query), "$options": "i"}
        match["$and"] = [{"$or": [
            {"item_name": rx},
            {"remark": rx},
        ]}]
    if year:
        match["year"] = int(year)
    if month:
        match["month"] = int(month)
    col = get_collection("market_records")
    return [serialize(d) for d in col.find(match).sort("purchase_date", -1).limit(int(limit))]


def last_purchase(item_name):
    """Most recent purchase of an item (for rate auto-fill)."""
    if not (item_name or "").strip():
        return None
    col = get_collection("market_records")
    doc = col.find_one(
        _base_match({"item_name": {"$regex": f"^{re.escape(item_name.strip())}$", "$options": "i"}}),
        sort=[("purchase_date", -1)])
    return serialize(doc)


def top_items(year, month, limit=5):
    """Top items of a month by spend, with bar percentages."""
    col = get_collection("market_records")
    rows = list(col.aggregate([
        {"$match": _base_match({"year": int(year), "month": int(month)})},
        {"$group": {"_id": "$item_name",
                    "amount": {"$sum": "$total"},
                    "qty": {"$sum": "$quantity"},
                    "count": {"$sum": 1}}},
        {"$sort": {"amount": -1}},
        {"$limit": int(limit)},
    ]))
    out = [{"item": r["_id"], "amount": round(r["amount"], 2),
            "qty": round(r["qty"], 2), "count": r["count"]} for r in rows]
    mx = max([o["amount"] for o in out] or [1])
    for o in out:
        o["pct"] = round(o["amount"] / mx * 100) if mx else 0
    return out


def popular_items(limit=8):
    """Most frequently purchased item names (search shortcuts)."""
    col = get_collection("market_records")
    rows = list(col.aggregate([
        {"$match": _base_match()},
        {"$group": {"_id": "$item_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": int(limit)},
    ]))
    return [r["_id"] for r in rows if r.get("_id")]
