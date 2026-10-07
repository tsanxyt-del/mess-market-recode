from django.apps import AppConfig


class MarketConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.market"

    def ready(self):
        # Indexes are ensured lazily (see database/indexes.py and first
        # Mongo access) so boot never blocks when MongoDB is down.
        from . import signals  # noqa: F401
