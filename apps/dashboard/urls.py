from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_dashboard, name="admin-dashboard"),
    path("api/stats/", views.admin_dashboard_api, name="admin-dashboard-api"),
]
