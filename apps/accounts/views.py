"""Accounts views: login / logout / profile / password."""
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect

from .forms import AdminLoginForm, ProfileForm, AdminPasswordChangeForm
from .services import update_profile, log_admin_event
from .validators import get_user_by_login


def login_view(request):
    if request.user.is_authenticated:
        return redirect("admin-dashboard")
    form = AdminLoginForm(request, data=request.POST or None)
    if request.method == "POST":
        login_input = request.POST.get("username", "").strip()
        user_obj = get_user_by_login(login_input)
        # If email was used, swap in the real username so AuthenticationForm works.
        if user_obj is not None:
            data = request.POST.copy()
            data["username"] = user_obj.username
            form = AdminLoginForm(request, data=data)
        if form.is_valid():
            auth_login(request, form.get_user())
            log_admin_event(f"Admin login: {request.user.username}", "login", username=request.user.username)
            nxt = request.GET.get("next") or "admin-dashboard"
            # Open-redirect guard: bahar ki site par kabhi mat bhejo.
            from django.utils.http import url_has_allowed_host_and_scheme
            if not url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
                nxt = "admin-dashboard"
            return redirect(nxt)
        messages.error(request, "Invalid username/email or password.")
    return render(request, "admin/login.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        log_admin_event(f"Admin logout: {request.user.username}", "logout", username=request.user.username)
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("admin-login")


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, initial={
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
    })
    if request.method == "POST" and form.is_valid():
        try:
            update_profile(request.user, **form.cleaned_data)
            messages.success(request, "Profile updated.")
            return redirect("admin-profile")
        except ValueError as exc:
            messages.error(request, str(exc))
    return render(request, "admin/profile/profile.html", {"form": form})


@login_required
def change_password_view(request):
    form = AdminPasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)
        messages.success(request, "Password changed successfully.")
        return redirect("admin-profile")
    return render(request, "admin/profile/change_password.html", {"form": form})


@login_required
def settings_view(request):
    return render(request, "admin/profile/settings.html")
