import requests
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_path = reverse(
        "activate-account",
        kwargs={
            "uidb64": uid,
            "token": token,
        },
    )

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")

    if request is not None:
        try:
            activation_url = request.build_absolute_uri(activation_path)
        except Exception:
            activation_url = f"{site_url}{activation_path}"
    else:
        activation_url = f"{site_url}{activation_path}"

    subject = "Activate your LangoMove account"

    try:
        text_body = render_to_string(
            "users/emails/verify_email.txt",
            {
                "user": user,
                "activation_url": activation_url,
            },
        )
    except Exception:
        text_body = (
            f"Hello {user.username},\n\n"
            f"Welcome to LangoMove.\n\n"
            f"Please confirm your email address by clicking the link below:\n\n"
            f"{activation_url}\n\n"
            f"If you did not create this account, you can safely ignore this email.\n"
        )

    html_body = text_body.replace("\n", "<br>")

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        },
        json={
            "sender": {
                "name": settings.BREVO_SENDER_NAME,
                "email": settings.BREVO_SENDER_EMAIL,
            },
            "to": [
                {
                    "email": user.email,
                    "name": user.username,
                }
            ],
            "subject": subject,
            "htmlContent": html_body,
            "textContent": text_body,
        },
        timeout=20,
    )

    response.raise_for_status()
