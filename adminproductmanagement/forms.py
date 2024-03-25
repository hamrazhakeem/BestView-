from django import forms
from .models import (
    Category,
    Brand,
    Product,
    ProductVariant,
    CategoryOffer,
    ProductOffer,
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = "__all__"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        exclude = ["offer_price"]

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = "__all__"
        exclude = ["product"]

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return quantity


class AddCategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = "__all__"
        exclude = ["category", "status"]


class AddProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = "__all__"
        exclude = ["product", "status"]
