from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from apps.users.forms import LoginForm, RegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("dashboard")

    return render(request, "users/register.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = LoginForm


def logout_view(request):
    logout(request)
    return redirect("home")