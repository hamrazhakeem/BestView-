from django import views
from django.urls import path
from . import views
from .views import payment_failed

app_name = "user_order_and_payment"

urlpatterns = [
    path("order_address/", views.order_address, name="order_address"),
    path("place_order/", views.place_order, name="place_order"),
    path("apply_coupon/", views.apply_coupon, name="apply_coupon"),
    path("payment_method/", views.payment_method, name="payment_method"),
    path("remove_coupon/", views.remove_coupon, name="remove_coupon"),
    path("payment_failed/", payment_failed.as_view(), name="payment_failed"),
]
