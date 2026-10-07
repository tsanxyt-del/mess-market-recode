"""Report pages + JSON API + exports (admin only)."""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from apps.items.services import list_items
from .monthly import monthly_report
from .daily import daily_report
from .item_wise import item_wise_report
from .export_excel import monthly_csv, daily_csv, itemwise_csv
from .export_excel import monthly_xlsx, daily_xlsx, itemwise_xlsx
from .export_pdf import monthly_pdf, daily_pdf, itemwise_pdf


def _default_ym(request):
    today = timezone.localdate()
    try:
        y = int(request.GET.get("year", today.year))
    except (TypeError, ValueError):
        y = today.year
    try:
        m = int(request.GET.get("month", today.month))
    except (TypeError, ValueError):
        m = today.month
    if not 1 <= m <= 12:
        m = today.month
    return y, m


def _empty_monthly(year, month):
    return {"year": year, "month": month, "total_amount": 0, "total_items": 0,
            "total_quantity": 0, "recorded_days": 0, "avg_daily": 0,
            "highest_day": None, "lowest_day": None, "days": []}


@login_required
def monthly_view(request):
    year, month = _default_ym(request)
    fmt = request.GET.get("format", "html")
    try:
        report = monthly_report(year, month)
        db_down = False
    except Exception:
        report, db_down = _empty_monthly(year, month), True
    if fmt == "csv":
        return monthly_csv(report)
    if fmt == "xlsx":
        return monthly_xlsx(report)
    if fmt == "pdf":
        return monthly_pdf(report)
    report["max_amount"] = max([1] + [float(d["amount"]) for d in report["days"]])
    return render(request, "admin/reports/monthly.html",
                  {"report": report, "year": year, "month": month, "db_down": db_down})


@login_required
def daily_view(request):
    date_str = request.GET.get("date", timezone.localdate().strftime("%Y-%m-%d"))
    fmt = request.GET.get("format", "html")
    try:
        report = daily_report(date_str)
        db_down = False
    except Exception:
        report = {"date": date_str, "display": date_str, "items": [],
                  "total_items": 0, "total_amount": 0, "total_quantity": 0}
        db_down = True
    if fmt == "csv":
        return daily_csv(report)
    if fmt == "xlsx":
        return daily_xlsx(report)
    if fmt == "pdf":
        return daily_pdf(report)
    return render(request, "admin/reports/daily.html",
                  {"report": report, "date_str": date_str, "db_down": db_down})


@login_required
def itemwise_view(request):
    item = request.GET.get("item", "")
    year = request.GET.get("year") or None
    month = request.GET.get("month") or None
    fmt = request.GET.get("format", "html")
    try:
        items_all = list_items(active_only=False)
    except Exception:
        items_all = []
    try:
        report = item_wise_report(item, year, month) if item else None
        db_down = False
    except Exception:
        report, db_down = None, True
    if report and fmt == "csv":
        return itemwise_csv(report)
    if report and fmt == "xlsx":
        return itemwise_xlsx(report)
    if report and fmt == "pdf":
        return itemwise_pdf(report)
    return render(request, "admin/reports/item_wise.html",
                  {"report": report, "item": item, "items": items_all,
                   "year": year or "", "month": month or "", "db_down": db_down})


@login_required
def export_view(request):
    return render(request, "admin/reports/export.html")


@require_GET
@login_required
def reports_api(request):
    kind = request.GET.get("kind", "monthly")
    try:
        if kind == "daily":
            return JsonResponse({"ok": True, "report": daily_report(
                request.GET.get("date", timezone.localdate().strftime("%Y-%m-%d")))})
        if kind == "item":
            return JsonResponse({"ok": True, "report": item_wise_report(
                request.GET.get("item", ""), request.GET.get("year") or None,
                request.GET.get("month") or None)})
        year, month = _default_ym(request)
        return JsonResponse({"ok": True, "report": monthly_report(year, month)})
    except Exception:
        return JsonResponse({"ok": False, "error": "Database unavailable."}, status=503)
