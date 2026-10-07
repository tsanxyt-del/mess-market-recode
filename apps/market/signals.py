"""Signal-ish hooks (called explicitly after writes)."""
import logging
from apps.accounts.services import log_admin_event

logger = logging.getLogger(__name__)


def record_created(record, username=""):
    try:
        log_admin_event(
            f"Purchase added: {record.get('item_name')} "
            f"{record.get('quantity')}{record.get('unit')} "
            f"₹{record.get('total')} on {record.get('purchase_date')}",
            "purchase_create", str(record.get("_id")), username)
    except Exception as exc:
        logger.warning("record_created hook failed: %s", exc)


def record_updated(record_id, username=""):
    try:
        log_admin_event(f"Purchase updated: {record_id}", "purchase_update", str(record_id), username)
    except Exception as exc:
        logger.warning("record_updated hook failed: %s", exc)


def record_deleted(record_id, username=""):
    try:
        log_admin_event(f"Purchase deleted: {record_id}", "purchase_delete", str(record_id), username)
    except Exception as exc:
        logger.warning("record_deleted hook failed: %s", exc)
