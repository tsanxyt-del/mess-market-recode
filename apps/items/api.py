from .views import items_api, items_api_admin

# Re-exported so config can wire /api/items/ if needed.
api = items_api
api_admin = items_api_admin
