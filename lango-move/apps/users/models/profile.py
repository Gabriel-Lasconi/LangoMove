from django.conf import settings
from django.db import models


class ClassParticipation(models.Model):
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="class_participations",
    )
    date = models.DateField()
    school_name = models.CharField(max_length=255)
    children_group = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=100)
    session_title = models.CharField(max_length=255, blank=True)

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes_as_teacher",
    )

    other_volunteers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="classes_as_teammate",
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.volunteer.username} - {self.school_name} - {self.date}"