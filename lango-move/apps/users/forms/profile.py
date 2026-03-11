from django import forms

from apps.users.models import User


class UserAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "photo",
            "date_of_birth",
            "phone",
            "city",
            "country",
            "bio",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "country": forms.TextInput(attrs={"placeholder": "Country"}),
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us a bit about yourself"}),
        }