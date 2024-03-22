from django import views
from django.urls import path
from . import views


app_name = "adminproductmanagement"

urlpatterns = [
    path("manage_category/", views.manage_category, name="manage_category"),
    path("add_category/", views.add_category, name="add_category"),
    path("edit_category/<int:pk>/", views.edit_category, name="edit_category"),
    path("delete_category/<int:pk>/", views.delete_category, name="delete_category"),
    path("unlist_category/<int:pk>/", views.unlist_category, name="unlist_category"),
    path("unlisted_categories", views.unlisted_categories, name="unlisted_categories"),
    path("restore_category/<int:pk>/", views.restore_category, name="restore_category"),
    path("manage_brand/", views.manage_brand, name="manage_brand"),
    path("add_brand/", views.add_brand, name="add_brand"),
    path("edit_brand/<int:pk>/", views.edit_brand, name="edit_brand"),
    path("delete_brand/<int:pk>/", views.delete_brand, name="delete_brand"),
    path("unlist_brand/<int:pk>/", views.unlist_brand, name="unlist_brand"),
    path("unlisted_brands", views.unlisted_brands, name="unlisted_brands"),
    path("restore_brand/<int:pk>/", views.restore_brand, name="restore_brand"),
    path("manage_product/", views.manage_product, name="manage_product"),
    path("add_product/", views.add_product, name="add_product"),
    path("edit_product/<int:pk>", views.edit_product, name="edit_product"),
    path("delete_product/<int:pk>/", views.delete_product, name="delete_product"),
    path("unlist_product/<int:pk>/", views.unlist_product, name="unlist_product"),
    path("unlisted_products", views.unlisted_products, name="unlisted_products"),
    path("restore_product/<int:pk>/", views.restore_product, name="restore_product"),
    path("add_variant/<int:product_id>/", views.add_variant, name="add_variant"),
    path("edit_variant/<int:pk>/", views.edit_variant, name="edit_variant"),
    path("delete_variant/<int:pk>/", views.delete_variant, name="delete_variant"),
    path(
        "delete_variant_image/<int:pk>/",
        views.delete_variant_image,
        name="delete_variant_image",
    ),
    path(
        "delete_product_thumbnail/<int:pk>/",
        views.delete_product_thumbnail,
        name="delete_product_thumbnail",
    ),
    path(
        "add_category_offer/<int:category_id>/",
        views.add_category_offer,
        name="add_category_offer",
    ),
    path(
        "delete_category_offer/<int:offer_id>/",
        views.delete_category_offer,
        name="delete_category_offer",
    ),
    path(
        "edit_category_offer/<int:offer_id>/",
        views.edit_category_offer,
        name="edit_category_offer",
    ),
    path(
        "add_product_offer/<int:product_id>/",
        views.add_product_offer,
        name="add_product_offer",
    ),
    path(
        "delete_product_offer/<int:offer_id>/",
        views.delete_product_offer,
        name="delete_product_offer",
    ),
    path(
        "edit_product_offer/<int:offer_id>/",
        views.edit_product_offer,
        name="edit_product_offer",
    ),
]
