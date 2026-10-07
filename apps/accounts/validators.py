"""Username/email authentication helpers."""
from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_by_login(login):
    """Allow login with username OR email."""
    login = (login or "").strip()
    if not login:
        return None
    try:
        if "@" in login:
            return User.objects.filter(email__iexact=login).order_by("id").first()
        return User.objects.filter(username__iexact=login).order_by("id").first()
    except Exception:
        return None


def validate_login_identifier(value):
    if not value or not value.strip():
        raise ValueError("Username or email is required.")
    return value.strip()
