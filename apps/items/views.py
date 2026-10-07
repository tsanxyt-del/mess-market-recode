"""Item admin views + JSON API."""
import json
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from config.mongo import DB_DOWN_MESSAGE
from apps.market.permissions import admin_api_required
from .forms import ItemForm
from .constants import CATEGORIES
from .services import (list_items, get_item, create_item, update_item,
                       set_active, delete_item, seed_default_items)
from .validators import ItemValidationError

logger = logging.getLogger(__name__)


def _db_error_message(request, exc, where):
    """Log technical detail, show only a friendly message to the user."""
    logger.warning("MongoDB unavailable in %s: %r", where, exc)
    messages.error(request, DB_DOWN_MESSAGE)


@login_required
def item_list(request):
    q = request.GET.get("q", "").strip()
    show = request.GET.get("show", "active")  # active | all | disabled
    cat = request.GET.get("cat", "").strip()
    try:
        items = list_items(active_only=False, search=q, category=cat)
        db_down = False
    except Exception:
        items = []
        db_down = True
    if show == "active":
        items = [i for i in items if i.get("is_active")]
    elif show == "disabled":
        items = [i for i in items if not i.get("is_active")]
    from collections import Counter
    cat_counts = dict(sorted(Counter((i.get("category") or "Other") for i in items).items()))
    return render(request, "admin/items/list.html",
                  {"items": items, "q": q, "show": show, "cat": cat,
                   "categories": CATEGORIES, "db_down": db_down,
                   "cat_counts": cat_counts})


@login_required
def item_add(request):
    form = ItemForm(request.POST or None)
    db_down = False
    if request.method == "POST" and form.is_valid():
        try:
            create_item(form.cleaned_data["name"], form.cleaned_data["default_unit"],
                        form.cleaned_data.get("category", "Other"),
                        form.cleaned_data.get("aliases", ""))
            messages.success(request, "Item added.")
            return redirect("item-list")
        except ItemValidationError as exc:
            messages.error(request, str(exc))
        except Exception as exc:
            # MongoDB down (ServerSelectionTimeoutError) must NOT 500.
            db_down = True
            _db_error_message(request, exc, "item_add")
    return render(request, "admin/items/add.html", {"form": form, "db_down": db_down})


@login_required
def item_edit(request, item_id):
    try:
        item = get_item(item_id)
    except Exception as exc:
        _db_error_message(request, exc, "item_edit:get")
        messages.error(request, "Item not found.")
        return redirect("item-list")
    if not item:
        messages.error(request, "Item not found.")
        return redirect("item-list")
    form = ItemForm(request.POST or None, initial={"name": item["name"],
                                                   "default_unit": item.get("default_unit", "KG"),
                                                   "category": item.get("category", "Other"),
                                                   "aliases": ", ".join(item.get("aliases") or [])})
    if request.method == "POST" and form.is_valid():
        try:
            update_item(item_id, form.cleaned_data["name"], form.cleaned_data["default_unit"],
                        form.cleaned_data.get("category", "Other"),
                        form.cleaned_data.get("aliases", ""))
            messages.success(request, "Item updated.")
            return redirect("item-list")
        except ItemValidationError as exc:
            messages.error(request, str(exc))
        except Exception as exc:
            _db_error_message(request, exc, "item_edit:save")
    return render(request, "admin/items/edit.html", {"form": form, "item": item})


@login_required
def item_toggle(request, item_id):
    if request.method != "POST":
        return redirect("item-list")
    try:
        item = get_item(item_id)
    except Exception as exc:
        _db_error_message(request, exc, "item_toggle:get")
        return redirect("item-list")
    if item:
        try:
            set_active(item_id, not item.get("is_active"))
            messages.success(request, "Item status updated.")
        except Exception as exc:
            _db_error_message(request, exc, "item_toggle:set")
    return redirect("item-list")


@login_required
def item_delete_view(request, item_id):
    try:
        item = get_item(item_id)
    except Exception as exc:
        _db_error_message(request, exc, "item_delete:get")
        return redirect("item-list")
    if not item:
        messages.error(request, "Item not found.")
        return redirect("item-list")
    if request.method == "POST":
        try:
            delete_item(item_id)
            messages.success(request, "Item deleted.")
        except ItemValidationError as exc:
            messages.error(request, str(exc))
        except Exception as exc:
            _db_error_message(request, exc, "item_delete")
        return redirect("item-list")
    return render(request, "admin/items/delete.html", {"item": item})


@login_required
def item_seed(request):
    try:
        n = seed_default_items()
        messages.success(request, f"Seeded {n} default items.")
    except Exception as exc:
        _db_error_message(request, exc, "item_seed")
    return redirect("item-list")


@login_required
def item_bulk_add(request):
    """Ek saath kayi items jodo — har line: Name, UNIT, Category (unit/category optional)."""
    from .constants import CATEGORIES as _CATS
    from apps.market.constants import UNIT_VALUES as _UNITS
    result = None
    if request.method == "POST":
        text = request.POST.get("bulk_text", "")
        try:
            ok, skipped, errors = 0, 0, []
            for lineno, line in enumerate(text.splitlines(), 1):
                line = line.strip().strip("-,*•")
                if not line:
                    continue
                parts = [p.strip() for p in line.split(",")]
                nm = parts[0] if len(parts) > 0 else ""
                un = (parts[1] if len(parts) > 1 else "KG").upper() or "KG"
                ct = parts[2] if len(parts) > 2 else "Other"
                if un not in _UNITS:
                    errors.append(f"Line {lineno}: unit '{un}' galat hai.")
                    continue
                if ct not in _CATS:
                    ct = "Other"
                try:
                    from .services import create_item as _create
                    _create(nm, un, ct)
                    ok += 1
                except ItemValidationError as exc:
                    skipped += 1
                    errors.append(f"Line {lineno} chhoda: {exc}")
            result = {"ok": ok, "skipped": skipped, "errors": errors[:20]}
            if ok:
                messages.success(request, f"{ok} items jud gaye.")
            if not ok and not errors:
                messages.error(request, "Koi line samajh nahi aayi — har line me naam likho.")
        except Exception as exc:
            _db_error_message(request, exc, "item_bulk_add")
            result = {"ok": 0, "skipped": 0, "errors": [DB_DOWN_MESSAGE]}
    return render(request, "admin/items/bulk_add.html",
                  {"result": result, "categories": _CATS})


@require_GET
def items_api(request):
    """Public dropdown API (active items only, searchable)."""
    q = request.GET.get("q", "")
    try:
        return JsonResponse({"ok": True, "items": list_items(active_only=True, search=q)})
    except Exception as exc:
        logger.warning("MongoDB unavailable in items_api: %r", exc)
        return JsonResponse({"ok": False, "error": DB_DOWN_MESSAGE}, status=503)


@admin_api_required
def items_api_admin(request):
    if request.method == "POST":
        try:
            try:
                payload = json.loads(request.body or "{}")
            except json.JSONDecodeError:
                return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)
            new_id = create_item(payload.get("name", ""), payload.get("default_unit", "KG"),
                                 payload.get("category", "Other"),
                                 payload.get("aliases", ""))
            return JsonResponse({"ok": True, "id": new_id})
        except ItemValidationError as exc:
            return JsonResponse({"ok": False, "error": str(exc)}, status=400)
        except Exception as exc:
            logger.warning("MongoDB unavailable in items_api_admin: %r", exc)
            return JsonResponse({"ok": False, "error": DB_DOWN_MESSAGE}, status=503)
    try:
        return JsonResponse({"ok": True, "items": list_items(active_only=False)})
    except Exception as exc:
        logger.warning("MongoDB unavailable in items_api_admin:list: %r", exc)
        return JsonResponse({"ok": False, "error": DB_DOWN_MESSAGE}, status=503)
