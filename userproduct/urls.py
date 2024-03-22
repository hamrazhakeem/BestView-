from django import views
from django.urls import path
from . import views

app_name = "userproduct"

urlpatterns = [
    path("product_details/<int:pk>/", views.product_details, name="product_details"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("cart/<int:cart_id>/", views.cart, name="cart"),
    path(
        "delete_from_cart/<int:variant_id>/",
        views.delete_from_cart,
        name="delete_from_cart",
    ),
    path("clear_cart/<int:cart_id>/", views.clear_cart, name="clear_cart"),
    path("update_cart_item/", views.update_cart_item, name="update_cart_item"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("add_to_wishlist/", views.add_to_wishlist, name="add_to_wishlist"),
    path(
        "delete-wishlist-item/", views.delete_wishlist_item, name="delete-wishlist-item"
    ),
]
