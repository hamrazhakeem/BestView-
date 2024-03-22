from django import views
from django.urls import path
from . import views

app_name = "userprofile"

urlpatterns = [
    path("profile/<int:user_id>/", views.profile, name="profile"),
    path("edit_profile/<int:user_id>", views.edit_profile, name="edit_profile"),
    path("change_password/", views.change_password, name="change_password"),
    path("address/", views.address, name="address"),
    path("add_address/", views.add_address, name="add_address"),
    path("add_address/<str:address_type>/", views.add_address, name="add_address"),
    path("edit_address/<int:address_id>", views.edit_address, name="edit_address"),
    path(
        "delete_address/<int:address_id>", views.delete_address, name="delete_address"
    ),
    path("orders/", views.orders, name="orders"),
    path("cancel_order/<int:item_id>/", views.cancel_order, name="cancel_order"),
    path("delete_account/<int:user_id>/", views.delete_account, name="delete_account"),
    path("return_order/<int:item_id>/", views.return_order, name="return_order"),
    path("wallet/", views.wallet, name="wallet"),
    path("cash_deposit_page/", views.cash_deposit_page, name="cash_deposit_page"),
    path("deposit/", views.deposit, name="deposit"),
    path("cash_withdraw_page/", views.cash_withdraw_page, name="cash_withdraw_page"),
    path("withdraw/", views.withdraw, name="withdraw"),
    path("transaction_history/", views.transaction_history, name="transaction_history"),
    path("coupon/", views.coupon, name="coupon"),
    path(
        "download_invoice/<int:item_id>/",
        views.download_invoice,
        name="download_invoice",
    ),
]
