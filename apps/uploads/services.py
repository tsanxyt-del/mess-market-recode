"""Upload services — orphan scan + listing helpers."""
from config.mongo import get_collection


def list_bill_records(limit=100):
    col = get_collection("market_records")
    docs = list(col.find({"bill_file": {"$ne": ""}, "deleted_at": None})
                .sort("purchase_date", -1).limit(int(limit)))
    out = []
    for d in docs:
        out.append({"id": str(d["_id"]),
                    "item_name": d.get("item_name", ""),
                    "purchase_date": d.get("purchase_date"),
                    "bill_file": d.get("bill_file", "")})
    return out


def referenced_bill_paths():
    col = get_collection("market_records")
    return {d.get("bill_file") for d in
            col.find({"bill_file": {"$ne": ""}}, {"bill_file": 1}) if d.get("bill_file")}
