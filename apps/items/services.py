"""Item CRUD on MongoDB `items` collection."""
import re
from datetime import datetime, timezone
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from config.mongo import get_collection
from .validators import validate_item_name, validate_default_unit, validate_category, validate_aliases, ItemValidationError
from .constants import DEFAULT_ITEMS, HINDI_ALIASES


def _now():
    return datetime.now(timezone.utc)


def _serialize(doc):
    if not doc:
        return None
    d = dict(doc)
    d["id"] = str(d.pop("_id"))
    for k in ("created_at", "updated_at"):
        v = d.get(k)
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    # Hindi-first display for admin: "Aloo (Potato)".
    aliases = [str(a) for a in (d.get("aliases") or []) if str(a).strip()]
    d["aliases"] = aliases
    name = str(d.get("name", ""))
    primary = next((a for a in aliases if a.lower() != name.lower()), "")
    d["hi"] = primary
    d["display_hi"] = f"{primary} ({name})" if primary else name
    d["hi_more"] = [a for a in aliases if a != primary and a.lower() != name.lower()]
    return d


def list_items(active_only=False, search="", category=""):
    q = {}
    if active_only:
        q["is_active"] = True
    if search:
        rx = {"$regex": re.escape(search.strip()), "$options": "i"}
        q["$or"] = [{"name": rx}, {"aliases": rx}]
    if category:
        q["category"] = category
    return [_serialize(d) for d in get_collection("items").find(q).sort("name", 1)]


def get_item(item_id):
    try:
        oid = ObjectId(item_id)
    except Exception:
        return None
    return _serialize(get_collection("items").find_one({"_id": oid}))


def resolve_item_name(name):
    """Hindi/alias typed naam → (canonical_name, item_id, default_unit).

    "aloo" → ("Potato", id, "KG"). No match → None. Never raises
    (DB down hone par None, caller apna normal flow chalaye).
    """
    try:
        key = (name or "").strip()
        if not key:
            return None
        col = get_collection("items")
        doc = col.find_one({"name_lower": key.lower()})
        if not doc:
            doc = col.find_one({"aliases": {"$regex": f"^{re.escape(key)}$",
                                            "$options": "i"}})
        if not doc:
            return None
        s = _serialize(doc)
        return {"name": s["name"], "id": s["id"],
                "unit": s.get("default_unit", "KG")}
    except Exception:
        return None


def create_item(name, default_unit="KG", category="Other", aliases=None):
    name = validate_item_name(name)
    unit = validate_default_unit(default_unit)
    category = validate_category(category)
    aliases = validate_aliases(aliases)
    try:
        res = get_collection("items").insert_one({
            "name": name, "name_lower": name.lower(), "default_unit": unit,
            "category": category, "aliases": aliases,
            "is_active": True, "created_at": _now(), "updated_at": _now(),
        })
    except DuplicateKeyError:
        raise ItemValidationError(f"Item '{name}' already exists.")
    return str(res.inserted_id)


def update_item(item_id, name=None, default_unit=None, category=None, aliases=None):
    try:
        oid = ObjectId(item_id)
    except Exception:
        raise ItemValidationError("Invalid item id.")
    patch = {"updated_at": _now()}
    if name is not None:
        name = validate_item_name(name)
        patch["name"] = name
        patch["name_lower"] = name.lower()
    if default_unit is not None:
        patch["default_unit"] = validate_default_unit(default_unit)
    if category is not None:
        patch["category"] = validate_category(category)
    if aliases is not None:
        patch["aliases"] = validate_aliases(aliases)
    try:
        get_collection("items").update_one({"_id": oid}, {"$set": patch})
    except DuplicateKeyError:
        raise ItemValidationError(f"Item '{name}' already exists.")
    return True


def set_active(item_id, active):
    try:
        oid = ObjectId(item_id)
    except Exception:
        raise ItemValidationError("Invalid item id.")
    get_collection("items").update_one(
        {"_id": oid}, {"$set": {"is_active": bool(active), "updated_at": _now()}})
    return True


def delete_item(item_id):
    try:
        oid = ObjectId(item_id)
    except Exception:
        raise ItemValidationError("Invalid item id.")
    get_collection("items").delete_one({"_id": oid})
    return True


def seed_default_items():
    """Idempotent seed of the default item master (adds aliases + backfills)."""
    col = get_collection("items")
    created = 0
    for entry in DEFAULT_ITEMS:
        name, unit = entry[0], entry[1]
        category = entry[2] if len(entry) > 2 else "Other"
        aliases = list(HINDI_ALIASES.get(name, []))
        try:
            # check-then-insert keeps seed idempotent even before indexes exist
            existing = col.find_one({"name_lower": name.lower()})
            if existing:
                # backfill Hindi aliases for items seeded before aliases existed
                if aliases and not existing.get("aliases"):
                    col.update_one({"_id": existing["_id"]},
                                   {"$set": {"aliases": aliases, "updated_at": _now()}})
                continue
            col.insert_one({"name": name, "name_lower": name.lower(),
                            "default_unit": unit, "category": category,
                            "aliases": aliases,
                            "is_active": True,
                            "created_at": _now(), "updated_at": _now()})
            created += 1
        except DuplicateKeyError:
            continue
    return created
