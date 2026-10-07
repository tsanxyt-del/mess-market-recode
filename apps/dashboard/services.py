"""Dashboard aggregates — today + current month + recent purchases."""
from django.utils import timezone
from config.mongo import get_collection
from apps.market.selectors import _base_match, serialize, month_summary, top_items


def today_str():
    return timezone.localdate().strftime("%Y-%m-%d")


def admin_stats():
    from datetime import datetime as _dt
    today = timezone.localdate()
    now = timezone.localtime()
    col = get_collection("market_records")
    # Mongo stores naive purchase_date; use naive local-midnight (Asia/Kolkata),
    # not server-local datetime.now(), so UTC hosts don't shift the day.
    day_start = _dt(today.year, today.month, today.day)
    today_docs = list(col.find(_base_match({"purchase_date": day_start})))
    today_total = round(sum(float(d.get("total", 0)) for d in today_docs), 2)
    ms = month_summary(now.year, now.month)
    recent = [serialize(d) for d in col.find(_base_match()).sort("created_at", -1).limit(8)]
    try:
        top5 = top_items(now.year, now.month, 5)
    except Exception:
        top5 = []
    return {
        "today_total": today_total,
        "today_items": len(today_docs),
        "today_date": now.strftime("%d %B %Y"),
        "month_total": ms["total_amount"],
        "month_items": ms["total_items"],
        "recorded_days": ms["recorded_days"],
        "avg_daily": ms.get("avg_daily", 0),
        "days": ms.get("days", []),
        "month_name": now.strftime("%B %Y"),
        "recent": recent,
        "top_items": top5,
    }
