from django.apps import apps
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

    @property
    def classrooms_as_teacher(self):
        return self.managed_classrooms.all()

    @property
    def classrooms_as_volunteer(self):
        return [assignment.classroom for assignment in self.classroom_assignments.filter(is_active=True)]

    @property
    def teacher_schools(self):
        School = apps.get_model("schools", "School")
        return School.objects.filter(
            teacher_memberships__teacher=self,
            teacher_memberships__is_active=True,
        ).distinct()

    @property
    def volunteer_schools(self):
        School = apps.get_model("schools", "School")
        return School.objects.filter(
            classrooms__volunteer_assignments__volunteer=self,
            classrooms__volunteer_assignments__is_active=True,
        ).distinct()

    @property
    def teacher_classrooms(self):
        Classroom = apps.get_model("schools", "Classroom")
        return Classroom.objects.filter(
            teacher=self,
            is_active=True,
        ).distinct()

    @property
    def volunteer_classrooms(self):
        Classroom = apps.get_model("schools", "Classroom")
        return Classroom.objects.filter(
            volunteer_assignments__volunteer=self,
            volunteer_assignments__is_active=True,
            is_active=True,
        ).distinct()

    @property
    def related_schools(self):
        if self.role == UserRole.TEACHER:
            return self.teacher_schools
        if self.role == UserRole.VOLUNTEER:
            return self.volunteer_schools
        if self.role == UserRole.ADMIN:
            School = apps.get_model("schools", "School")
            return School.objects.all()
        return []

    @property
    def related_classrooms(self):
        if self.role == UserRole.TEACHER:
            return self.teacher_classrooms
        if self.role == UserRole.VOLUNTEER:
            return self.volunteer_classrooms
        if self.role == UserRole.ADMIN:
            Classroom = apps.get_model("schools", "Classroom")
            return Classroom.objects.all()
        return []

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"