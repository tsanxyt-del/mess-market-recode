"""Global template context."""
from django.conf import settings


def site_info(request):
    return {
        "site_name": "Mess Market Record",
        "currency": "₹",
        "app_version": getattr(settings, "APP_VERSION", "4.6"),
    }
