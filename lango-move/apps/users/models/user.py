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

    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        self.is_staff = self.role == UserRole.ADMIN
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"