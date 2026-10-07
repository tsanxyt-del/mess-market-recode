"""Root URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.dashboard.views import robots_view

_admin_path = getattr(settings, "DJANGO_ADMIN_PATH", "django-admin/")
if not _admin_path.endswith("/"):
    _admin_path += "/"

urlpatterns = [
    path("robots.txt", robots_view, name="robots"),
    path(_admin_path, admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("panel/market/", include("apps.market.urls")),
    path("panel/items/", include("apps.items.urls")),
    path("panel/reports/", include("apps.reports.urls")),
    path("panel/uploads/", include("apps.uploads.urls")),
    path("panel/activity/", include("apps.notifications.urls")),
    path("panel/", include("apps.dashboard.urls")),
    path("", include("apps.dashboard.public_urls")),
]

handler404 = "apps.dashboard.views.handler404"
handler500 = "apps.dashboard.views.handler500"

# MEDIA bills ko prod me bhi serve karo (Render disk). Bade scale par nginx/S3
# behtar hai, par chhote mess setup ke liye Django serving kaafi hai.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
