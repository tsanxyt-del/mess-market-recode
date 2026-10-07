"""Monthly report logic — aggregation over market_records."""
from apps.market.selectors import month_summary


def monthly_report(year, month):
    s = month_summary(int(year), int(month))
    return {
        "year": int(year), "month": int(month),
        "total_amount": s["total_amount"],
        "total_items": s["total_items"],
        "total_quantity": s["total_quantity"],
        "recorded_days": s["recorded_days"],
        "avg_daily": s["avg_daily"],
        "highest_day": s["highest_day"],
        "lowest_day": s["lowest_day"],
        "days": s["days"],
    }
