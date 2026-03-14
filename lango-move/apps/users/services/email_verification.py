from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    print("=== EMAIL VERIFICATION DEBUG ===")
    print("USER PK:", user.pk)
    print("UID:", uid)
    print("TOKEN:", token)

    activation_path = reverse(
        "activate-account",
        kwargs={
            "uidb64": uid,
            "token": token,
        },
    )
    print("ACTIVATION PATH:", activation_path)

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    print("SITE_URL:", site_url)

    if request is not None:
        try:
            activation_url = request.build_absolute_uri(activation_path)
        except Exception as exc:
            print("build_absolute_uri failed:", exc)
            activation_url = f"{site_url}{activation_path}"
    else:
        activation_url = f"{site_url}{activation_path}"

    print("ACTIVATION URL:", activation_url)

    subject = "Activate your LangoMove account"

    try:
        message = render_to_string(
            "users/emails/verify_email.txt",
            {
                "user": user,
                "activation_url": activation_url,
            },
        )
    except Exception as exc:
        print("render_to_string failed:", exc)
        message = (
            f"Hello {user.username},\n\n"
            f"Welcome to LangoMove.\n\n"
            f"Please confirm your email address by clicking the link below:\n\n"
            f"{activation_url}\n\n"
            f"If you did not create this account, you can safely ignore this email.\n"
        )

    print("EMAIL_BACKEND USED:", settings.EMAIL_BACKEND)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    print("\n" + "=" * 80)
    print("ACTIVATION LINK:")
    print(activation_url)
    print("=" * 80 + "\n")