from django import views
from django.urls import path
from . import views


app_name = "admin_order_and_payment"

urlpatterns = [
    path("manage_order/", views.manage_order, name="manage_order"),
    path(
        "manage_order_status/<int:item_id>/",
        views.manage_order_status,
        name="manage_order_status",
    ),
    path(
        "update_order_status/<int:item_id>/",
        views.update_order_status,
        name="update_order_status",
    ),
]
