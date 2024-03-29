from django import forms
from .models import Banner
from adminproductmanagement.models import Coupons


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = "__all__"


class AddCouponForm(forms.ModelForm):
    class Meta:
        model = Coupons
        fields = "__all__"

    def clean_minimum_amount(self):
        minimum_amount = self.cleaned_data.get("minimum_amount")
        if minimum_amount is not None and minimum_amount < 0:
            raise forms.ValidationError("Minimum amount cannot be negative.")
        return minimum_amount

    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get("discount_percentage")
        if discount_percentage is not None and discount_percentage < 0:
            raise forms.ValidationError("Discount percentage cannot be negative.")
        return discount_percentage
