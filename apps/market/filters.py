"""Build Mongo filters from GET params (shared by views + API)."""
from .constants import DEFAULT_PAGE_SIZE


def parse_list_params(params):
    def _int(key, default=None):
        try:
            v = params.get(key)
            return int(v) if v not in (None, "") else default
        except (TypeError, ValueError):
            return default

    def _float(key):
        try:
            v = params.get(key)
            return float(v) if v not in (None, "") else None
        except (TypeError, ValueError):
            return None

    filters = {
        "q": (params.get("q") or "").strip(),
        "item": (params.get("item") or "").strip(),
        "unit": (params.get("unit") or "").strip(),
        "date": (params.get("date") or "").strip(),
        "date_from": (params.get("date_from") or "").strip(),
        "date_to": (params.get("date_to") or "").strip(),
    }
    y, m = _int("year"), _int("month")
    if y:
        filters["year"] = y
    if m:
        filters["month"] = m
    mn, mx = _float("min_amount"), _float("max_amount")
    if mn is not None:
        filters["min_amount"] = mn
    if mx is not None:
        filters["max_amount"] = mx
    page = _int("page", 1) or 1
    page_size = _int("page_size", DEFAULT_PAGE_SIZE) or DEFAULT_PAGE_SIZE
    sort = params.get("sort", "-purchase_date")
    return filters, page, page_size, sort
