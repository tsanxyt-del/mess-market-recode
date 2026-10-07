"""Public pages (no login) + admin dashboard + error handlers."""
import logging
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from apps.market.selectors import (month_summary, day_records, available_months,
                                    search_public, popular_items)
from apps.market.constants import MONTH_NAMES
from .services import admin_stats

logger = logging.getLogger(__name__)


def manifest_view(request):
    """Serve PWA manifest from site root (required scope/start_url)."""
    from django.conf import settings
    from django.http import FileResponse, Http404
    path = settings.BASE_DIR / "static" / "manifest.json"
    if not path.exists():
        raise Http404("manifest not found")
    return FileResponse(open(path, "rb"), content_type="application/manifest+json")


def sw_view(request):
    """Serve service worker from site root so its scope covers all pages."""
    from django.conf import settings
    from django.http import FileResponse, Http404
    path = settings.BASE_DIR / "static" / "sw.js"
    if not path.exists():
        raise Http404("service worker not found")
    return FileResponse(open(path, "rb"), content_type="application/javascript")

EMPTY_SUMMARY = {
    "total_amount": 0, "total_items": 0, "total_quantity": 0,
    "recorded_days": 0, "days": [], "avg_daily": 0,
    "highest_day": None, "lowest_day": None,
}


def _db_unavailable(request, exc, where):
    # Log only; public pages degrade gracefully with db_down=True.
    logger.warning("MongoDB unavailable in %s: %s", where, exc)


# ---------- Public ----------

def public_index(request):
    today = timezone.localdate()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
    except (TypeError, ValueError):
        year, month = today.year, today.month
    if not 1 <= month <= 12:
        year, month = today.year, today.month
    try:
        from apps.market.selectors import top_items
        summary = month_summary(year, month)
        months = available_months()
        try:
            top = top_items(year, month, 8)
        except Exception:
            top = []
        db_down = False
    except Exception as exc:
        _db_unavailable(request, exc, "public_index")
        summary, months = dict(EMPTY_SUMMARY), []
        top = []
        db_down = True
    year_total = round(sum(m["amount"] for m in months if m["year"] == year), 2)
    all_total = round(sum(m["amount"] for m in months), 2)
    ctx = {
        "year": year, "month": month, "month_name": MONTH_NAMES[month],
        "summary": summary, "months": months, "db_down": db_down,
        "top_items": top,
        "year_total": year_total,
        "all_total": all_total,
        "total_months": len(months),
        "year_months": [m for m in months if m["year"] == year],
        "years": sorted({m["year"] for m in months}, reverse=True) or [today.year],
        "month_names": MONTH_NAMES,
        "month_list": [(i, MONTH_NAMES[i]) for i in range(1, 13)],
    }
    return render(request, "public/index.html", ctx)


def public_months(request):
    try:
        months = available_months()
        db_down = False
    except Exception as exc:
        _db_unavailable(request, exc, "public_months")
        months = []
        db_down = True
    # group by year (newest year first) with year totals
    groups = []
    for m in months:
        if not groups or groups[-1]["year"] != m["year"]:
            groups.append({"year": m["year"], "months": [], "items": 0, "amount": 0.0})
        g = groups[-1]
        g["months"].append(m)
        g["items"] += m["items"]
        g["amount"] = round(g["amount"] + m["amount"], 2)
    grand_total = round(sum(m["amount"] for m in months), 2)
    grand_items = sum(m["items"] for m in months)
    max_amount = max([m["amount"] for m in months] or [0])
    return render(request, "public/months.html",
                  {"months": months, "groups": groups, "db_down": db_down,
                   "grand_total": grand_total, "grand_items": grand_items,
                   "max_amount": max_amount})


def public_month_detail(request, year, month):
    try:
        y, m = int(year), int(month)
    except (TypeError, ValueError):
        return render(request, "public/404.html", status=404)
    if not 1 <= m <= 12:
        return render(request, "public/404.html", status=404)
    try:
        from apps.market.selectors import top_items
        summary = month_summary(y, m)
        try:
            top = top_items(y, m, 8)
        except Exception:
            top = []
        db_down = False
    except Exception as exc:
        _db_unavailable(request, exc, "public_month_detail")
        summary = dict(EMPTY_SUMMARY)
        top = []
        db_down = True
    return render(request, "public/month_detail.html", {
        "year": y, "month": m, "db_down": db_down,
        "top_items": top,
        "prev_y": (y - 1) if m == 1 else y, "prev_m": 12 if m == 1 else m - 1,
        "next_y": (y + 1) if m == 12 else y, "next_m": 1 if m == 12 else m + 1,
        "month_name": MONTH_NAMES[m], "summary": summary})


def public_day_detail(request, date_str):
    from datetime import timedelta
    if date_str == "today":
        from django.shortcuts import redirect as _redirect
        return _redirect("public-day-detail", date_str=timezone.localdate().strftime("%Y-%m-%d"))
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return render(request, "public/404.html", status=404)
    prev_day = (dt - timedelta(days=1)).strftime("%Y-%m-%d")
    next_day = (dt + timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        data = day_records(date_str)
        db_down = False
    except Exception as exc:
        _db_unavailable(request, exc, "public_day_detail")
        data = {"date": date_str, "display": date_str, "items": [],
                "total_items": 0, "total_amount": 0, "total_quantity": 0}
        db_down = True
    # Insight: aaj ka kharcha is mahine ke ausat se kitna upar/neeche.
    vs_avg = None
    try:
        avg = month_summary(dt.year, dt.month).get("avg_daily", 0)
        if avg and data.get("total_amount"):
            pct = round((data["total_amount"] - avg) / avg * 100)
            if abs(pct) < 5:
                vs_avg = {"text": f"Mahine ke ausat (₹{avg:g}) ke barabar", "cls": "even"}
            elif pct > 0:
                vs_avg = {"text": f"Ausat se {pct}% zyada (ausat ₹{avg:g})", "cls": "up"}
            else:
                vs_avg = {"text": f"Ausat se {abs(pct)}% kam (ausat ₹{avg:g})", "cls": "down"}
    except Exception:
        vs_avg = None
    return render(request, "public/day_detail.html",
                  {"data": data, "db_down": db_down, "vs_avg": vs_avg,
                   "prev_day": prev_day, "next_day": next_day})


def public_search(request):
    q = request.GET.get("q", "").strip()
    try:
        results = search_public(q) if q else []
        popular = popular_items(8)
        db_down = False
    except Exception as exc:
        _db_unavailable(request, exc, "public_search")
        results = []
        popular = []
        db_down = True
    return render(request, "public/search.html",
                  {"q": q, "results": results, "popular": popular, "db_down": db_down})


def public_ledger(request):
    """Date-wise full khata: har entry date ke saath (filter + page)."""
    from apps.market.filters import parse_list_params
    from apps.market.selectors import list_records, records_summary
    filters, page, page_size, sort = parse_list_params(request.GET)
    # Ledger me zyada rows dikhao, date-wise naya pehle.
    if not request.GET.get("page_size"):
        page_size = 30
    if not request.GET.get("sort"):
        sort = "-purchase_date"
    try:
        data = list_records(filters, page, page_size, sort)
        items = data["items"]
        page_total = round(sum(float(i.get("total", 0) or 0) for i in items), 2)
        try:
            summ = records_summary(filters)
        except Exception:
            summ = {"total_amount": page_total, "total_count": data["total"],
                    "days_count": 0}
        db_down = False
    except Exception as exc:
        _db_unavailable(request, exc, "public_ledger")
        data = {"items": [], "total": 0, "page": 1, "pages": 1, "page_size": page_size}
        items, page_total = [], 0
        summ = {"total_amount": 0, "total_count": 0, "days_count": 0}
        db_down = True
    # Range label: "3 Oct – 5 Oct" jaisa, ya filter ke hisab se.
    from datetime import datetime as _dt
    def _fmt(ds):
        try:
            return _dt.strptime(ds, "%Y-%m-%d").strftime("%d %b")
        except (TypeError, ValueError):
            return ""
    df, dt = filters.get("date_from", ""), filters.get("date_to", "")
    if df and dt:
        range_label = f"{_fmt(df)} – {_fmt(dt)}"
    elif df:
        range_label = f"{_fmt(df)} ke baad"
    elif dt:
        range_label = f"{_fmt(dt)} tak"
    elif filters.get("q"):
        range_label = f"“{filters['q']}” search"
    else:
        range_label = "Sab dates"
    # Compact page window
    try:
        pg, pgs = int(data["page"]), int(data["pages"])
    except (TypeError, ValueError):
        pg, pgs = 1, 1
    start = max(1, pg - 2)
    end = min(pgs, pg + 2)
    page_range = list(range(start, end + 1))
    # Keep filters in pagination links
    qd = request.GET.copy()
    qd.pop("page", None)
    query = qd.urlencode()
    # Date-wise groups with subtotals (page ki entries, order barkarar).
    groups = []
    for it in items:
        key = it.get("purchase_date", "")
        if not groups or groups[-1]["date"] != key:
            groups.append({"date": key,
                           "display": it.get("purchase_date_display") or key,
                           "items": [], "subtotal": 0.0, "count": 0})
        g = groups[-1]
        g["items"].append(it)
        g["count"] += 1
        try:
            g["subtotal"] = round(g["subtotal"] + float(it.get("total", 0) or 0), 2)
        except (TypeError, ValueError):
            pass
    return render(request, "public/ledger.html", {
        "items": items, "total": data["total"], "page": pg, "pages": pgs,
        "page_size": data["page_size"], "page_range": page_range,
        "page_total": page_total, "query": query, "groups": groups,
        "range_total": summ["total_amount"], "range_count": summ["total_count"],
        "range_days": summ["days_count"], "range_label": range_label,
        "f": request.GET, "db_down": db_down,
    })


def public_reports(request):
    today = timezone.localdate()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
    except (TypeError, ValueError):
        year, month = today.year, today.month
    if not 1 <= month <= 12:
        year, month = today.year, today.month
    try:
        from apps.market.selectors import top_items, available_months
        summary = month_summary(year, month)
        try:
            top = top_items(year, month, 10)
        except Exception:
            top = []
        try:
            months = available_months()
            year_total = round(sum(m["amount"] for m in months if m["year"] == year), 2)
            years = sorted({m["year"] for m in months}, reverse=True) or [today.year]
        except Exception:
            year_total, years = 0, [today.year]
        db_down = False
    except Exception as exc:
        _db_unavailable(request, exc, "public_reports")
        summary = dict(EMPTY_SUMMARY)
        top = []
        year_total, years = 0, [today.year]
        db_down = True
    return render(request, "public/reports.html", {
        "summary": summary, "year": year, "month": month, "db_down": db_down,
        "top_items": top, "year_total": year_total, "years": years,
        "month_list": [(i, MONTH_NAMES[i]) for i in range(1, 13)],
        "month_name": MONTH_NAMES[month]})


def handler404(request, exception=None):
    return render(request, "public/404.html", status=404)


def handler500(request):
    return render(request, "public/500.html", status=500)


def robots_view(request):
    # Stealth: never advertise /panel/, /accounts/ or admin paths.
    from django.http import HttpResponse
    lines = [
        "User-agent: *",
        "Allow: /",
        "Allow: /months/",
        "Allow: /month/",
        "Allow: /day/",
        "Allow: /search/",
        "Allow: /ledger/",
        "Allow: /reports/",
        "Disallow: /panel/",
        "Disallow: /accounts/",
        "Disallow: /django-admin/",
        "Disallow: /mgmt-admin/",
        "Disallow: /static/admin/",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


# ---------- Admin ----------

@login_required
def admin_dashboard(request):
    from config.mongo import ping
    try:
        stats = admin_stats()
        db_down = False
    except Exception:
        stats = {"today_total": 0, "today_items": 0, "today_date": "",
                 "month_total": 0, "month_items": 0, "recorded_days": 0,
                 "month_name": "", "recent": []}
        db_down = True
    stats["db_ok"] = (not db_down) and ping()
    return render(request, "admin/dashboard.html", {"stats": stats, "db_down": db_down})


@require_GET
@login_required
def admin_dashboard_api(request):
    try:
        return JsonResponse({"ok": True, "stats": admin_stats()})
    except Exception as exc:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)
