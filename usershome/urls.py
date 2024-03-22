from django import views
from django.urls import path
from . import views
from .views import about_us

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.signin, name="signin"),
    path("register/", views.signup, name="signup"),
    path("otpverify/", views.verify_otp, name="verify_otp"),
    path("logout/", views.signout, name="signout"),
    path("shop/", views.shop, name="shop"),
    path("about_us/", about_us.as_view(), name="about_us"),
    path("filter_products/", views.filter_products, name="filter_products"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path(
        "forgot_password_verify_otp/",
        views.forgot_password_verify_otp,
        name="forgot_password_verify_otp",
    ),
    path(
        "forgot_change_password/",
        views.forgot_change_password,
        name="forgot_change_password",
    ),
    path("del_info/", views.del_info, name="del_info"),
    path("privacy_policy/", views.privacy_policy, name="privacy_policy"),
    path(
        "terms_and_conditions/", views.terms_and_conditions, name="terms_and_conditions"
    ),
    path("customer_service", views.customer_service, name="customer_service"),
    path("contact_us/", views.contact_us, name="contact_us"),
]
