from django import views
from django.urls import path
from . import views


app_name = "adminshome"

urlpatterns = [
    path("adminsignin/", views.adminsignin, name="adminsignin"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("adminsignout/", views.adminsignout, name="adminsignout"),
    path("manage_banner/", views.manage_banner, name="manage_banner"),
    path("add_banner/", views.add_banner, name="add_banner"),
    path("edit_banner/<int:pk>/", views.edit_banner, name="edit_banner"),
    path("delete_banner/<int:pk>/", views.delete_banner, name="delete_banner"),
    path("manage_coupon/", views.manage_coupon, name="manage_coupon"),
    path("unlist_coupon/<int:coupon_id>", views.unlist_coupon, name="unlist_coupon"),
    path("unlisted_coupons/", views.unlisted_coupons, name="unlisted_coupons"),
    path("list_coupon/<int:coupon_id>", views.list_coupon, name="list_coupon"),
    path("add_coupon/", views.add_coupon, name="add_coupon"),
    path("download_pdf/", views.download_pdf, name="download_pdf"),
    path("get_revenue_data/", views.get_revenue_data, name="get_revenue_data"),
    path("get_data/", views.get_data, name="get_data"),
]
