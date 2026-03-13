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

    activation_url = request.build_absolute_uri(
        reverse(
            "activate-account",
            kwargs={
                "uidb64": uid,
                "token": token,
            },
        )
    )

    subject = "Activate your LangoMove account"

    message = render_to_string(
        "users/emails/verify_email.txt",
        {
            "user": user,
            "activation_url": activation_url,
        },
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    if settings.DEBUG:
        print("\n" + "=" * 80)
        print("DEV ACTIVATION LINK:")
        print(activation_url)
        print("=" * 80 + "\n")