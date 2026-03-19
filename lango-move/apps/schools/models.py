from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from apps.curriculum.models import AgeGroup, Course, CourseTopic, Topic
from apps.users.models import User, UserRole


def generate_unique_slug(model_class, value, instance_pk=None):
    base_slug = slugify(value) or "item"
    slug = base_slug
    counter = 2

    queryset = model_class.objects.all()
    if instance_pk:
        queryset = queryset.exclude(pk=instance_pk)

    while queryset.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


class School(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    city = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(School, self.name, self.pk)
        super().save(*args, **kwargs)


class Classroom(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="classrooms",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    age_group = models.ForeignKey(
        AgeGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classrooms",
    )
    academic_year = models.CharField(max_length=20, blank=True)
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_classrooms",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classrooms",
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("school__name", "name")
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name", "academic_year"],
                name="unique_classroom_per_school_and_year",
            ),
        ]

    def __str__(self):
        year = f" ({self.academic_year})" if self.academic_year else ""
        return f"{self.school.name} - {self.name}{year}"

    def clean(self):
        if self.teacher and self.teacher.role != UserRole.TEACHER:
            raise ValidationError({"teacher": "Selected user must have the teacher role."})

        if self.course and self.age_group and self.course.age_group_id and self.course.age_group_id != self.age_group_id:
            raise ValidationError(
                {"course": "Selected course does not match the classroom age group."}
            )

        if self.course and self.school and not self.school.is_active:
            raise ValidationError({"school": "You cannot assign a course to an inactive school."})

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_value = f"{self.school.name}-{self.name}-{self.academic_year or 'classroom'}"
            self.slug = generate_unique_slug(Classroom, slug_value, self.pk)
        self.full_clean()
        super().save(*args, **kwargs)


class ClassroomVolunteerAssignment(models.Model):
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="volunteer_assignments",
    )
    volunteer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="classroom_assignments",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("classroom__school__name", "classroom__name", "volunteer__username")
        constraints = [
            models.UniqueConstraint(
                fields=["classroom", "volunteer"],
                name="unique_volunteer_per_classroom",
            ),
        ]

    def __str__(self):
        return f"{self.volunteer} → {self.classroom}"

    def clean(self):
        if self.volunteer and self.volunteer.role != UserRole.VOLUNTEER:
            raise ValidationError({"volunteer": "Selected user must have the volunteer role."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class TeacherSchoolMembership(models.Model):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_school_memberships",
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="teacher_memberships",
    )
    is_primary = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "school"],
                name="unique_teacher_school_membership",
            ),
        ]
        ordering = ("teacher__username", "school__name")

    def __str__(self):
        return f"{self.teacher} @ {self.school}"

    def clean(self):
        if self.teacher and self.teacher.role != UserRole.TEACHER:
            raise ValidationError({"teacher": "Selected user must have the teacher role."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class EvaluationLevel(models.IntegerChoices):
    VERY_WEAK = 1, "Very weak"
    WEAK = 2, "Weak"
    AVERAGE = 3, "Average"
    GOOD = 4, "Good"
    VERY_GOOD = 5, "Very good"


class ClassTopicEvaluation(models.Model):
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="topic_evaluations",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="class_evaluations",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_evaluations",
    )
    course_topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_evaluations",
    )
    evaluated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_class_evaluations",
    )

    evaluation_date = models.DateField()

    score_participation = models.PositiveSmallIntegerField(
        choices=EvaluationLevel.choices,
        null=True,
        blank=True,
    )
    score_comprehension = models.PositiveSmallIntegerField(
        choices=EvaluationLevel.choices,
        null=True,
        blank=True,
    )
    score_speaking = models.PositiveSmallIntegerField(
        choices=EvaluationLevel.choices,
        null=True,
        blank=True,
    )
    score_behavior = models.PositiveSmallIntegerField(
        choices=EvaluationLevel.choices,
        null=True,
        blank=True,
    )

    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    follow_up_needed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-evaluation_date", "-created_at")

    def __str__(self):
        return f"{self.classroom} - {self.topic} - {self.evaluation_date}"

    def clean(self):
        errors = {}

        if self.evaluated_by and self.evaluated_by.role not in [
            UserRole.TEACHER,
            UserRole.VOLUNTEER,
            UserRole.ADMIN,
        ]:
            errors["evaluated_by"] = "Only teacher, volunteer, or admin can submit evaluations."

        if self.classroom_id:
            classroom_course = self.classroom.course

            if self.course_id and classroom_course and self.course_id != classroom_course.id:
                errors["course"] = "Selected course must match the course assigned to the classroom."

            if self.course_topic_id and classroom_course and self.course_topic.course_id != classroom_course.id:
                errors["course_topic"] = "Selected course topic does not belong to the classroom course."

            if self.course_topic_id and self.course_id and self.course_topic.course_id != self.course_id:
                errors["course_topic"] = "Selected course topic does not belong to the selected course."

            if (
                self.evaluated_by
                and self.evaluated_by.role == UserRole.TEACHER
                and self.classroom.teacher_id != self.evaluated_by.id
            ):
                errors["classroom"] = "Teachers can only evaluate classrooms they teach."

            if self.evaluated_by and self.evaluated_by.role == UserRole.VOLUNTEER:
                is_assigned = ClassroomVolunteerAssignment.objects.filter(
                    classroom=self.classroom,
                    volunteer=self.evaluated_by,
                    is_active=True,
                ).exists()
                if not is_assigned:
                    errors["classroom"] = "Volunteers can only evaluate classrooms they are assigned to."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.classroom and self.classroom.course:
            self.course = self.classroom.course
        self.full_clean()
        super().save(*args, **kwargs)