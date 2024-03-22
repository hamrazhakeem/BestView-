from django import forms
from usershome.models import CustomUser
from .models import Address


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name"]


class AddAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "house_or_building_name",
            "street_address",
            "city",
            "district",
            "pincode",
            "state",
            "phone_no",
        ]

        def clean_house_or_building_name(self):
            house_or_building_name = self.cleaned_data.get("house_or_building_name")
            # Check if house_or_building_name contains any digits
            if any(char.isdigit() for char in house_or_building_name):
                raise forms.ValidationError(
                    "House or building name cannot contain numbers."
                )
            return house_or_building_name
