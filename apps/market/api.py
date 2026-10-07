"""JSON APIs: public (read-only) + admin (write, auth required)."""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from apps.items.services import list_items
from .filters import parse_list_params
from .permissions import admin_api_required
from .selectors import (list_records, get_record, month_summary, day_records,
                        available_months, available_years, search_public,
                        last_purchase)
from .services import create_record, update_record, soft_delete_record
from .signals import record_created, record_updated, record_deleted
from .validators import MarketValidationError


@require_GET
def api_months(request):
    try:
        return JsonResponse({"ok": True, "months": available_months(), "years": available_years()})
    except Exception:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)


@require_GET
def api_month_detail(request, year, month):
    try:
        return JsonResponse({"ok": True, "year": int(year), "month": int(month),
                             "summary": month_summary(int(year), int(month))})
    except ValueError:
        return JsonResponse({"ok": False, "error": "Invalid year/month."}, status=400)
    except Exception:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)


@require_GET
def api_day_detail(request, date_str):
    from datetime import datetime as _dt
    try:
        _dt.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return JsonResponse({"ok": False, "error": "Invalid date. Use YYYY-MM-DD."}, status=400)
    try:
        return JsonResponse({"ok": True, **day_records(date_str)})
    except Exception:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)


@require_GET
def api_search(request):
    q = request.GET.get("q", "").strip()
    try:
        return JsonResponse({"ok": True, "results": search_public(
            q, request.GET.get("year") or None, request.GET.get("month") or None)})
    except Exception:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)


@require_GET
def api_records(request):
    """Public paginated records (read-only subset of admin list)."""
    filters, page, page_size, sort = parse_list_params(request.GET)
    try:
        return JsonResponse({"ok": True, **list_records(filters, page, page_size, sort)})
    except Exception:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)


@require_GET
def api_items_for_dropdown(request):
    q = request.GET.get("q", "")
    try:
        return JsonResponse({"ok": True, "items": list_items(active_only=True, search=q)})
    except Exception:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)


@require_GET
def api_item_last(request):
    """Last purchase of an item — powers rate auto-fill (admin form)."""
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "Authentication required."}, status=401)
    try:
        return JsonResponse({"ok": True, "last": last_purchase(request.GET.get("name", ""))})
    except Exception:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)


@admin_api_required
@require_POST
def api_create(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)
    try:
        rec = create_record(
            purchase_date=payload.get("purchase_date", ""),
            item_id=payload.get("item_id", ""), item_name=payload.get("item_name", ""),
            quantity=payload.get("quantity", 0), unit=payload.get("unit", "KG"),
            rate=payload.get("rate", 0), remark=payload.get("remark", ""))
        record_created(rec, request.user.username)
        doc = dict(rec)
        _id = doc.pop("_id", None)
        return JsonResponse({"ok": True, "id": str(_id), "total": rec["total"]})
    except MarketValidationError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    except Exception:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)


@admin_api_required
@require_POST
def api_update(request, record_id):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)
    try:
        allowed = {k: payload[k] for k in
                   ("purchase_date", "item_id", "item_name", "quantity", "unit", "rate", "remark", "bill_file")
                   if k in payload}
        update_record(record_id, **allowed)
        record_updated(record_id, request.user.username)
        return JsonResponse({"ok": True, "record": get_record(record_id)})
    except MarketValidationError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    except Exception:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)


@admin_api_required
@require_POST
def api_delete(request, record_id):
    try:
        soft_delete_record(record_id)
        record_deleted(record_id, request.user.username)
        return JsonResponse({"ok": True})
    except MarketValidationError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    except Exception:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)
