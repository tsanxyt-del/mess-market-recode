"""Admin Market CRUD views (HTML)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from config.mongo import DB_DOWN_MESSAGE
from apps.items.services import list_items
from apps.uploads.storage import save_bill_file, delete_bill_file
from .filters import parse_list_params
from .forms import PurchaseForm
from .selectors import list_records, get_record
from .services import create_record, update_record, soft_delete_record
from .signals import record_created, record_updated, record_deleted
from .validators import MarketValidationError


def _page_range(page, pages, window=2):
    """Compact page window, e.g. page 7 of 20 -> [5,6,7,8,9]."""
    try:
        page, pages = int(page), int(pages)
    except (TypeError, ValueError):
        return [1]
    start = max(1, page - window)
    end = min(pages, page + window)
    return list(range(start, end + 1))


@login_required
def purchase_list(request):
    from django.http import JsonResponse
    from django.template.loader import render_to_string
    filters, page, page_size, sort = parse_list_params(request.GET)
    try:
        data = list_records(filters, page, page_size, sort)
        db_down = False
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("MongoDB unavailable in purchase_list: %s", exc)
        data = {"items": [], "total": 0, "page": 1, "pages": 1, "page_size": page_size}
        db_down = True
    ctx = {
        "records": data["items"], "total": data["total"], "page": data["page"],
        "pages": data["pages"], "page_size": data["page_size"], "db_down": db_down,
        "page_range": _page_range(data["page"], data["pages"]),
        "page_sum": round(sum(float(i.get("total", 0) or 0) for i in data["items"]), 2),
        "filters": request.GET, "sort": sort,
    }
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # Return table + pagination + meta together so filters never leave stale UI.
        return JsonResponse({
            "ok": True,
            "table": render_to_string("admin/market/_table.html", ctx, request=request),
            "pagination": render_to_string("admin/includes/pagination.html", ctx, request=request),
            "total": ctx["total"], "page": ctx["page"], "pages": ctx["pages"],
            "page_sum": ctx["page_sum"],
        })
    return render(request, "admin/market/list.html", ctx)


@login_required
def purchase_add(request):
    try:
        items = list_items(active_only=True)
        db_down = False
    except Exception:
        items = []
        db_down = True
    # One-tap repeat: haal ki khareedo me se unique items (latest rate ke saath).
    recent_chips = []
    try:
        from .selectors import list_records as _list
        seen = set()
        for r in _list({}, 1, 20, "-created_at")["items"]:
            nm = (r.get("item_name") or "").strip()
            if not nm or nm.lower() in seen:
                continue
            seen.add(nm.lower())
            recent_chips.append({"name": nm, "unit": r.get("unit", "KG"),
                                 "rate": r.get("rate", "")})
            if len(recent_chips) >= 10:
                break
    except Exception:
        recent_chips = []
    initial = {}
    if request.GET.get("date"):
        initial["purchase_date"] = request.GET.get("date")
    copy_from = request.GET.get("copy")
    if copy_from and request.method != "POST":
        try:
            src = get_record(copy_from)
        except Exception:
            src = None
        if src:
            from datetime import date as _date
            initial = {"purchase_date": _date.today().strftime("%Y-%m-%d"),
                       "item_id": src.get("item_id", ""),
                       "item_name": src.get("item_name", ""),
                       "quantity": src.get("quantity", ""),
                       "unit": src.get("unit", "KG"),
                       "rate": src.get("rate", ""),
                       "remark": src.get("remark", "")}
    form = PurchaseForm(request.POST or None, request.FILES or None,
                        initial=initial or None)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        bill_path = ""
        try:
            if cd.get("bill_file"):
                bill_path = save_bill_file(cd["bill_file"], cd["purchase_date"])
            rec = create_record(
                purchase_date=cd["purchase_date"].strftime("%Y-%m-%d"),
                item_id=cd.get("item_id", ""), item_name=cd["item_name"],
                quantity=cd["quantity"], unit=cd["unit"], rate=cd["rate"],
                bill_file=bill_path, remark=cd.get("remark", ""))
            record_created(rec, request.user.username)
            messages.success(request, f"Purchase saved — total ₹{rec['total']:,.2f}.")
            if request.POST.get("save_and_add"):
                date_s = cd["purchase_date"].strftime("%Y-%m-%d")
                return redirect(reverse("market-add") + f"?date={date_s}&saved=1")
            return redirect("market-list")
        except MarketValidationError as exc:
            messages.error(request, str(exc))
        except ValueError as exc:
            messages.error(request, str(exc))
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("MongoDB unavailable in purchase_add: %r", exc)
            messages.error(request, DB_DOWN_MESSAGE)
    return render(request, "admin/market/add.html",
                  {"form": form, "items": items, "editing": False,
                   "db_down": db_down, "recent_chips": recent_chips,
                   "copy_mode": bool(copy_from and request.method != "POST"),
                   "saved_again": request.GET.get("saved") == "1"})


@login_required
def purchase_detail(request, record_id):
    try:
        rec = get_record(record_id)
    except Exception:
        rec = None
    if not rec:
        messages.error(request, "Record not found.")
        return redirect("market-list")
    return render(request, "admin/market/detail.html", {"rec": rec})


@login_required
def purchase_edit(request, record_id):
    try:
        rec = get_record(record_id)
    except Exception:
        rec = None
    if not rec:
        messages.error(request, "Record not found.")
        return redirect("market-list")
    try:
        items = list_items(active_only=True)
    except Exception:
        items = []
    if request.method == "POST":
        form = PurchaseForm(request.POST, request.FILES or None)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                bill_path = rec.get("bill_file", "")
                if cd.get("bill_file"):
                    if bill_path:
                        delete_bill_file(bill_path)
                    bill_path = save_bill_file(cd["bill_file"], cd["purchase_date"])
                update_record(record_id,
                              purchase_date=cd["purchase_date"].strftime("%Y-%m-%d"),
                              item_id=cd.get("item_id", ""), item_name=cd["item_name"],
                              quantity=cd["quantity"], unit=cd["unit"], rate=cd["rate"],
                              bill_file=bill_path, remark=cd.get("remark", ""))
                record_updated(record_id, request.user.username)
                messages.success(request, "Purchase updated.")
                return redirect("market-detail", record_id=record_id)
            except (MarketValidationError, ValueError) as exc:
                messages.error(request, str(exc))
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning("MongoDB unavailable in purchase_edit: %r", exc)
                messages.error(request, DB_DOWN_MESSAGE)
    else:
        form = PurchaseForm(initial={
            "purchase_date": rec.get("purchase_date"), "item_id": rec.get("item_id", ""),
            "item_name": rec.get("item_name"), "quantity": rec.get("quantity"),
            "unit": rec.get("unit"), "rate": rec.get("rate"), "remark": rec.get("remark", ""),
        })
    return render(request, "admin/market/edit.html", {"form": form, "rec": rec, "items": items, "editing": True})


@login_required
def purchase_delete(request, record_id):
    try:
        rec = get_record(record_id)
    except Exception:
        rec = None
    if not rec:
        messages.error(request, "Record not found.")
        return redirect("market-list")
    if request.method == "POST":
        try:
            soft_delete_record(record_id)
            record_deleted(record_id, request.user.username)
            messages.success(request, "Purchase deleted.")
        except MarketValidationError as exc:
            messages.error(request, str(exc))
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("MongoDB unavailable in purchase_delete: %r", exc)
            messages.error(request, DB_DOWN_MESSAGE)
        return redirect("market-list")
    return render(request, "admin/market/delete.html", {"rec": rec})
