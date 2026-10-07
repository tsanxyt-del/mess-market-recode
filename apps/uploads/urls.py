from django.urls import path
from . import views

urlpatterns = [
    path("bills/", views.bill_manager, name="bill-manager"),
]
