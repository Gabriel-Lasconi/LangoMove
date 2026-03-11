from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    GUEST = "guest", "Guest"
    TEACHER = "teacher", "Teacher"
    VOLUNTEER = "volunteer", "Volunteer"
    ADMIN = "admin", "Admin"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.GUEST,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        if self.role == UserRole.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"