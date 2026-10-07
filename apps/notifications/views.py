"""Admin activity log (reads MongoDB `notifications` audit collection)."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .services import recent_notifications


TYPE_META = {
    "login": ("🔵", "Login", "badge-blue"),
    "logout": ("⚫", "Logout", "badge-grey"),
    "purchase_create": ("🟢", "Purchase added", "badge-green"),
    "purchase_update": ("🟡", "Purchase updated", "badge-amber"),
    "purchase_delete": ("🔴", "Purchase deleted", "badge-red"),
}


@login_required
def activity_log(request):
    try:
        notes = recent_notifications(100)
        db_down = False
    except Exception:
        notes = []
        db_down = True
    for n in notes:
        icon, label, badge = TYPE_META.get(n.get("type", ""), ("📌", n.get("type", "event"), "badge-grey"))
        n["icon"], n["label"], n["badge"] = icon, label, badge
    return render(request, "admin/activity/log.html", {"notes": notes, "db_down": db_down})
