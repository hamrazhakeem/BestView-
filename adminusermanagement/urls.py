from django import views
from django.urls import path
from . import views


app_name = "adminusermanagement"

urlpatterns = [
    path("userlist/", views.userlist, name="userlist"),
    path(
        "block_unblock_user/<int:user_id>/",
        views.block_unblock_user,
        name="block_unblock_user",
    ),
]
