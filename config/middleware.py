"""Stealth + hardening middleware.

- Hides admin/panel URLs from search engines (X-Robots-Tag: noindex).
- Converts raw MongoDB outage into a friendly 503 page instead of a
  DEBUG traceback leaking SECRET_KEY / paths (defence in depth when
  DEBUG=True is left on locally).
- Adds security headers without breaking the PWA.
"""
import logging

logger = logging.getLogger(__name__)

# Backward-compat alias (old code/tests may import this).
ADMIN_PREFIXES = ("/panel/", "/accounts/", "/django-admin/", "/mgmt-admin/")


def _admin_prefixes():
    from django.conf import settings
    base = ("/panel/", "/accounts/")
    custom = str(getattr(settings, "DJANGO_ADMIN_PATH", "django-admin/") or "django-admin/")
    custom = "/" + custom.strip("/") + "/"
    defaults = {"/django-admin/", "/mgmt-admin/"}
    defaults.add(custom)
    return tuple(base) + tuple(sorted(defaults))


class StealthAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path or "/"
        if path.startswith(_admin_prefixes()):
            # Never index staff pages; never cache them on shared proxies.
            response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
            response["Cache-Control"] = "no-store, no-cache, must-revalidate"
        else:
            # Public pages are safe to cache briefly at edge.
            if response.status_code == 200 and "Cache-Control" not in response:
                response["Cache-Control"] = "public, max-age=60"
        # Clickjacking + MIME hardening (mirrors settings).
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("Referrer-Policy", "same-origin")
        return response

    def process_exception(self, request, exc):
        # Last-resort friendly page for DB outages — no topology dump.
        try:
            from config.mongo import is_db_error
            if is_db_error(exc):
                logger.warning("DB outage at %s: %r", request.path, exc)
                from django.shortcuts import render
                return render(
                    request, "public/503.html",
                    {"path": request.path}, status=503,
                )
        except Exception:
            pass
        return None
