from django import forms
from .models import Banner
from adminproductmanagement.models import Coupons


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = "__all__"


class AddCouponFrom(forms.ModelForm):
    class Meta:
        model = Coupons
        fields = "__all__"
