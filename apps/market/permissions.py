"""Permission helpers for function-based views."""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def admin_required(view):
    return login_required(view)


def admin_api_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"ok": False, "error": "Authentication required."}, status=401)
        return view(request, *args, **kwargs)
    return wrapper
