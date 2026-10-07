"""Notification read helpers."""
from config.mongo import get_collection


def recent_notifications(limit=20):
    docs = list(get_collection("notifications").find().sort("created_at", -1).limit(int(limit)))
    out = []
    for d in docs:
        d = dict(d)
        d["id"] = str(d.pop("_id"))
        v = d.get("created_at")
        if hasattr(v, "isoformat"):
            d["created_at"] = v.isoformat()
        out.append(d)
    return out


def mark_all_read():
    get_collection("notifications").update_many({"is_read": False}, {"$set": {"is_read": True}})
