from django.conf import settings
from django.db import models


class ClassParticipation(models.Model):
    # Legacy fields kept temporarily so existing records do not break.
    # New logic should use `volunteers`.
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="legacy_main_class_participations",
        null=True,
        blank=True,
    )
    other_volunteers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="legacy_other_class_participations",
    )

    # New unified volunteers field
    volunteers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="joined_class_participations",
    )

    date = models.DateField()

    # Legacy free-text fields kept for compatibility
    school_name = models.CharField(max_length=255)
    children_group = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=100)
    session_title = models.CharField(max_length=255, blank=True)

    # New relational fields
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_participations",
    )
    classroom = models.ForeignKey(
        "schools.Classroom",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="participations",
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes_as_teacher",
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        if self.classroom:
            return f"{self.classroom} - {self.date}"
        return f"{self.school_name} - {self.date}"

    @property
    def resolved_school_name(self):
        if self.school:
            return self.school.name
        if self.classroom and self.classroom.school:
            return self.classroom.school.name
        return self.school_name

    @property
    def resolved_children_group(self):
        if self.classroom and self.classroom.age_group:
            return self.classroom.age_group.label or self.classroom.age_group.name
        return self.children_group

    @property
    def all_volunteers(self):
        """
        Unified volunteer list.
        First tries the new `volunteers` field.
        Falls back to legacy `volunteer + other_volunteers` if needed.
        """
        seen = {}
        unified = list(self.volunteers.all())

        if unified:
            for user in unified:
                seen[user.id] = user
            return list(seen.values())

        if self.volunteer:
            seen[self.volunteer.id] = self.volunteer

        for user in self.other_volunteers.all():
            seen[user.id] = user

        return list(seen.values())