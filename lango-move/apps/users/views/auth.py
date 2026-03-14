import traceback

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from apps.users.forms.auth import RegisterForm
from apps.users.models import User
from apps.users.services.email_verification import send_verification_email


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()

            if not user.is_active:
                messages.error(
                    request,
                    "Your account is not activated yet. Please check your email or request a new activation link."
                )
                return redirect("resend-activation")

            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "users/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegisterForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            print("=== REGISTER DEBUG ===")
            print("DEBUG:", settings.DEBUG)
            print("EMAIL_BACKEND:", settings.EMAIL_BACKEND)
            print("DEFAULT_FROM_EMAIL:", settings.DEFAULT_FROM_EMAIL)
            print("SITE_URL:", getattr(settings, "SITE_URL", ""))
            print("USER ID:", user.id)
            print("USER EMAIL:", user.email)

            try:
                send_verification_email(request, user)
                messages.success(
                    request,
                    "Account created. Please check your email to activate it."
                )
                return redirect("registration-pending", user_id=user.id)
            except Exception:
                print("=== Activation email error during registration ===")
                traceback.print_exc()
                messages.warning(
                    request,
                    "Your account was created, but we could not send the activation email right now. "
                    "Please request a new activation link."
                )
                return redirect("resend-activation")

    return render(request, "users/register.html", {"form": form})


def registration_pending_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "users/registration_pending.html", {"pending_user": user})


def activate_account_view(request, uidb64, token):
    user = None

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None:
        messages.error(request, "We could not identify this account.")
        return redirect("resend-activation")

    if user.is_active:
        messages.info(request, "This account is already activated. You can log in.")
        return redirect("login")

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(
            request,
            "Your email has been confirmed. You can now log in to your account."
        )
        return redirect("login")

    return render(
        request,
        "users/activation_invalid.html",
        {
            "activation_email": user.email,
        },
        status=400,
    )


def resend_activation_view(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()

        if not email:
            messages.error(request, "Please enter your email address.")
            return redirect("resend-activation")

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = None

        if user is None:
            messages.error(request, "No account was found with that email address.")
            return redirect("resend-activation")

        if user.is_active:
            messages.info(request, "This account is already activated. You can log in.")
            return redirect("login")

        print("=== RESEND DEBUG ===")
        print("DEBUG:", settings.DEBUG)
        print("EMAIL_BACKEND:", settings.EMAIL_BACKEND)
        print("DEFAULT_FROM_EMAIL:", settings.DEFAULT_FROM_EMAIL)
        print("SITE_URL:", getattr(settings, "SITE_URL", ""))
        print("USER ID:", user.id)
        print("USER EMAIL:", user.email)

        try:
            send_verification_email(request, user)
            messages.success(
                request,
                "A new activation link has been sent to your email address."
            )
            return redirect("registration-pending", user_id=user.id)
        except Exception:
            print("=== Activation email error during resend ===")
            traceback.print_exc()
            messages.error(
                request,
                "We could not send a new activation email right now. Please try again later."
            )
            return redirect("resend-activation")

    return render(request, "users/resend_activation.html")


def logout_view(request):
    logout(request)
    return redirect("home")