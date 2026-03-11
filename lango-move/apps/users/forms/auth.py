from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from apps.users.models import User, UserRole


REGISTRATION_ROLE_CHOICES = [
    (UserRole.GUEST, "Guest"),
    (UserRole.TEACHER, "Teacher"),
    (UserRole.VOLUNTEER, "Volunteer"),
]


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=REGISTRATION_ROLE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")