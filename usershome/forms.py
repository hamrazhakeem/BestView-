from django import forms
from usershome.models import CustomUser
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ["first_name", "last_name", "username", "email"]


class LoginForm(forms.Form):
    username = forms.CharField(
        label="", widget=forms.TextInput(attrs={"placeholder": "Username"})
    )
    password = forms.CharField(
        label="", widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )


class ForgotPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        if password:
            if password.isdigit():
                raise forms.ValidationError("Password cannot be entirely numeric")

            if len(password) < 8:
                raise forms.ValidationError(
                    "Password must be at least 8 characters long"
                )

            commonly_used_passwords = ["password", "12345678"]
            if password.lower() in commonly_used_passwords:
                raise forms.ValidationError("Password is commonly used")

        return cleaned_data
