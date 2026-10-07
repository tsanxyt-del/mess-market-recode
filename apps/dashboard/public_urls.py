"""Public routes (no login required)."""
from django.urls import path
from . import views

urlpatterns = [
    path("manifest.json", views.manifest_view, name="pwa-manifest"),
    path("sw.js", views.sw_view, name="pwa-sw"),
    path("", views.public_index, name="public-index"),
    path("months/", views.public_months, name="public-months"),
    path("month/<int:year>/<int:month>/", views.public_month_detail, name="public-month-detail"),
    path("day/<str:date_str>/", views.public_day_detail, name="public-day-detail"),
    path("search/", views.public_search, name="public-search"),
    path("ledger/", views.public_ledger, name="public-ledger"),
    path("reports/", views.public_reports, name="public-reports"),
]
