from django.urls import path
from . import views

urlpatterns = [
    path("", views.item_list, name="item-list"),
    path("add/", views.item_add, name="item-add"),
    path("bulk-add/", views.item_bulk_add, name="item-bulk-add"),
    path("seed/", views.item_seed, name="item-seed"),
    path("<str:item_id>/edit/", views.item_edit, name="item-edit"),
    path("<str:item_id>/toggle/", views.item_toggle, name="item-toggle"),
    path("<str:item_id>/delete/", views.item_delete_view, name="item-delete"),
    path("api/list/", views.items_api, name="items-api"),
    path("api/admin/", views.items_api_admin, name="items-api-admin"),
]
