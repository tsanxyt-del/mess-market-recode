"""Write operations — create / update / soft-delete with backend totals."""
from datetime import datetime, timezone
from bson import ObjectId
from config.mongo import get_collection
from .validators import validate_record_payload, MarketValidationError


def _now():
    return datetime.now(timezone.utc)


def _canonicalize(item_name, item_id):
    """Alias typed naam ko master ke asli naam se badlo.

    "Aloo" → "Potato" (taaki reports me ek hi naam jude). Match na mile
    ya DB down ho to typed values waisi ki waisi — kabhi crash nahi.
    """
    try:
        from apps.items.services import resolve_item_name
        hit = resolve_item_name(item_name)
        if hit:
            item_name = hit["name"]
            if not (item_id or "").strip():
                item_id = hit["id"]
    except Exception:
        pass
    return item_name, item_id


def create_record(*, purchase_date, item_id="", item_name="", quantity=0,
                  unit="KG", rate=0, bill_file="", remark=""):
    item_name, item_id = _canonicalize(item_name, item_id)
    clean = validate_record_payload(item_id, item_name, quantity, unit, rate, purchase_date)
    doc = {
        **clean,
        "bill_file": bill_file or "",
        "remark": (remark or "").strip(),
        "created_at": _now(),
        "updated_at": _now(),
        "deleted_at": None,
    }
    res = get_collection("market_records").insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


def update_record(record_id, **kwargs):
    try:
        oid = ObjectId(record_id)
    except Exception:
        raise MarketValidationError("Invalid record id.")
    col = get_collection("market_records")
    existing = col.find_one({"_id": oid})
    if not existing or existing.get("deleted_at"):
        raise MarketValidationError("Record not found.")
    merged = {
        "item_id": kwargs.get("item_id", existing.get("item_id", "")),
        "item_name": kwargs.get("item_name", existing.get("item_name", "")),
        "quantity": kwargs.get("quantity", existing.get("quantity")),
        "unit": kwargs.get("unit", existing.get("unit", "KG")),
        "rate": kwargs.get("rate", existing.get("rate")),
        "purchase_date": kwargs.get("purchase_date", existing.get("purchase_date")),
    }
    if "item_name" in kwargs or "item_id" in kwargs:
        merged["item_name"], merged["item_id"] = _canonicalize(
            merged["item_name"], merged["item_id"])
    # bill_file / remark may be passed explicitly
    clean = validate_record_payload(**merged)
    update = {**clean,
              "bill_file": kwargs.get("bill_file", existing.get("bill_file", "")),
              "remark": (kwargs.get("remark", existing.get("remark", "")) or "").strip(),
              "updated_at": _now()}
    col.update_one({"_id": oid}, {"$set": update})
    return str(oid)


def soft_delete_record(record_id):
    try:
        oid = ObjectId(record_id)
    except Exception:
        raise MarketValidationError("Invalid record id.")
    res = get_collection("market_records").update_one(
        {"_id": oid}, {"$set": {"deleted_at": _now(), "updated_at": _now()}})
    if res.matched_count == 0:
        raise MarketValidationError("Record not found.")
    return True


def restore_record(record_id):
    try:
        oid = ObjectId(record_id)
    except Exception:
        raise MarketValidationError("Invalid record id.")
    get_collection("market_records").update_one(
        {"_id": oid}, {"$set": {"deleted_at": None, "updated_at": _now()}})
    return True


def hard_delete_record(record_id):
    try:
        oid = ObjectId(record_id)
    except Exception:
        raise MarketValidationError("Invalid record id.")
    get_collection("market_records").delete_one({"_id": oid})
    return True
