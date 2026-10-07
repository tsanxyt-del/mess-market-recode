from django.urls import path
from . import views

urlpatterns = [
    path("monthly/", views.monthly_view, name="report-monthly"),
    path("daily/", views.daily_view, name="report-daily"),
    path("item-wise/", views.itemwise_view, name="report-itemwise"),
    path("export/", views.export_view, name="report-export"),
    path("api/data/", views.reports_api, name="reports-api"),
]
