"""Account-related services (profile update + audit logging)."""
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def log_admin_event(message, event_type="admin", related_id=None, username=None):
    """Best-effort audit log into MongoDB notifications collection."""
    try:
        from config.mongo import get_collection
        get_collection("notifications").insert_one({
            "type": event_type,
            "message": message,
            "related_id": related_id,
            "username": username,
            "is_read": False,
            "created_at": datetime.now(timezone.utc),
        })
    except Exception as exc:
        logger.warning("Audit log failed: %s", exc)


def update_profile(user, first_name="", last_name="", email=""):
    user.first_name = (first_name or "").strip()
    user.last_name = (last_name or "").strip()
    email = (email or "").strip()
    if email:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.exclude(pk=user.pk).filter(email__iexact=email).exists():
            raise ValueError("This email is already used by another account.")
        user.email = email
    user.save(update_fields=["first_name", "last_name", "email"])
    return user
