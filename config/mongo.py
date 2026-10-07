"""Central MongoDB connection (PyMongo singleton) + index bootstrap."""
import logging
import os
from pymongo import MongoClient, ASCENDING

logger = logging.getLogger(__name__)

_client = None
_db = None
_indexes_started = False


def _ensure_async():
    try:
        ensure_indexes()
    except Exception:
        pass


def get_mongo_client():
    global _client
    if _client is None:
        from django.conf import settings
        _client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=10000,
            retryWrites=True,
        )
    return _client


def get_db():
    global _db
    if _db is None:
        from django.conf import settings
        _db = get_mongo_client()[settings.MONGODB_DATABASE]
    return _db


def get_collection(name):
    global _indexes_started
    if not _indexes_started:
        _indexes_started = True
        # Non-blocking: never slow down first request when MongoDB is down.
        import threading
        threading.Thread(target=_ensure_async, daemon=True).start()
    return get_db()[name]


def ensure_indexes():
    """Create indexes required for performance with thousands of records."""
    db = get_db()
    try:
        db.market_records.create_index([("purchase_date", ASCENDING)])
        db.market_records.create_index([("year", ASCENDING), ("month", ASCENDING)])
        db.market_records.create_index([("item_id", ASCENDING)])
        db.market_records.create_index([("created_at", ASCENDING)])
        db.market_records.create_index([("item_name", ASCENDING)])
        db.items.create_index("name_lower", unique=True)
        db.items.create_index("aliases")
        db.notifications.create_index([("created_at", ASCENDING)])
        logger.info("MongoDB indexes ensured.")
    except Exception as exc:  # never crash boot on index errors
        logger.warning("Could not ensure indexes: %s", exc)


def ping(timeout_ms=1500):
    """Fast liveness check — returns True/False, never raises."""
    try:
        # Honor caller timeout instead of blocking on client defaults (5-10s).
        get_mongo_client().admin.command("ping", maxTimeMS=int(timeout_ms))
        return True
    except Exception:
        # Fallback: short server-selection ping with explicit timeout.
        try:
            from pymongo import MongoClient
            from django.conf import settings
            tmp = MongoClient(settings.MONGODB_URI,
                              serverSelectionTimeoutMS=int(timeout_ms),
                              connectTimeoutMS=int(timeout_ms),
                              socketTimeoutMS=int(timeout_ms))
            try:
                tmp.admin.command("ping")
                return True
            finally:
                try:
                    tmp.close()
                except Exception:
                    pass
        except Exception:
            return False


# Friendly message shown when MongoDB is down — never expose raw
# ServerSelectionTimeoutError / topology details to end users.
DB_DOWN_MESSAGE = (
    "Database service is temporarily unavailable. "
    "Please try again in a moment — your data is safe."
)


def is_db_error(exc):
    """True for PyMongo connection / timeout errors (DB down, not a bug)."""
    try:
        from pymongo.errors import (
            ServerSelectionTimeoutError, AutoReconnect,
            NetworkTimeout, ConnectionFailure,
        )
        return isinstance(exc, (
            ServerSelectionTimeoutError, AutoReconnect,
            NetworkTimeout, ConnectionFailure,
        ))
    except Exception:
        pass
    # Fallback: match by name so callers don't need pymongo imports.
    name = type(exc).__name__
    return name in (
        "ServerSelectionTimeoutError", "AutoReconnect",
        "NetworkTimeout", "ConnectionFailure", "OperationFailure",
    )
