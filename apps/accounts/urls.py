from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="admin-login"),
    path("logout/", views.logout_view, name="admin-logout"),
    path("profile/", views.profile_view, name="admin-profile"),
    path("password/", views.change_password_view, name="admin-password"),
    path("settings/", views.settings_view, name="admin-settings"),
]
