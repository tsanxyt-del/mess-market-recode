from django.urls import path
from . import views, api

urlpatterns = [
    # JSON (api/ must come before <str:record_id>/ or "api" is treated as an id)
    path("api/records/", api.api_records, name="api-records"),
    path("api/months/", api.api_months, name="api-months"),
    path("api/month/<int:year>/<int:month>/", api.api_month_detail, name="api-month-detail"),
    path("api/day/<str:date_str>/", api.api_day_detail, name="api-day-detail"),
    path("api/search/", api.api_search, name="api-search"),
    path("api/items/", api.api_items_for_dropdown, name="api-items-dropdown"),
    path("api/item-last/", api.api_item_last, name="api-item-last"),
    path("api/create/", api.api_create, name="api-create"),
    path("api/<str:record_id>/update/", api.api_update, name="api-update"),
    path("api/<str:record_id>/delete/", api.api_delete, name="api-delete"),
    # HTML
    path("", views.purchase_list, name="market-list"),
    path("add/", views.purchase_add, name="market-add"),
    path("<str:record_id>/", views.purchase_detail, name="market-detail"),
    path("<str:record_id>/edit/", views.purchase_edit, name="market-edit"),
    path("<str:record_id>/delete/", views.purchase_delete, name="market-delete"),
]
