"""Daily report logic."""
from apps.market.selectors import day_records


def daily_report(date_str):
    return day_records(date_str)
