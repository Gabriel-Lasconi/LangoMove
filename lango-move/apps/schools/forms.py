from django import forms
from django.utils import timezone

from apps.schools.models import ClassTopicEvaluation, Classroom
from apps.curriculum.models import Course, CourseTopic, Topic
from apps.users.models import UserRole


class ClassTopicEvaluationForm(forms.ModelForm):
    class Meta:
        model = ClassTopicEvaluation
        fields = [
            "classroom",
            "topic",
            "course",
            "course_topic",
            "evaluation_date",
            "score_participation",
            "score_comprehension",
            "score_speaking",
            "score_behavior",
            "strengths",
            "weaknesses",
            "notes",
            "follow_up_needed",
        ]
        widgets = {
            "evaluation_date": forms.DateInput(attrs={"type": "date"}),
            "strengths": forms.Textarea(attrs={"rows": 3, "placeholder": "Strengths observed"}),
            "weaknesses": forms.Textarea(attrs={"rows": 3, "placeholder": "Weaknesses observed"}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Additional notes"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields["evaluation_date"].initial = timezone.now().date()
        self.fields["course"].required = False
        self.fields["course_topic"].required = False

        if not user:
            return

        allowed_classrooms = Classroom.objects.none()

        if user.role == UserRole.TEACHER:
            allowed_classrooms = Classroom.objects.filter(teacher=user)

        elif user.role == UserRole.VOLUNTEER:
            allowed_classrooms = Classroom.objects.filter(
                volunteer_assignments__volunteer=user,
                volunteer_assignments__is_active=True,
            )

        elif user.role == UserRole.ADMIN:
            allowed_classrooms = Classroom.objects.all()

        self.fields["classroom"].queryset = allowed_classrooms.distinct().select_related("school", "age_group")
        self.fields["topic"].queryset = Topic.objects.order_by("display_order", "name")
        self.fields["course"].queryset = Course.objects.order_by("title")
        self.fields["course_topic"].queryset = CourseTopic.objects.order_by("course__title", "sequence_number", "title")

    def clean(self):
        cleaned_data = super().clean()
        classroom = cleaned_data.get("classroom")

        if self.user and classroom:
            if self.user.role == UserRole.TEACHER and classroom.teacher_id != self.user.id:
                raise forms.ValidationError("You can only evaluate your own classes.")

            if self.user.role == UserRole.VOLUNTEER:
                is_assigned = classroom.volunteer_assignments.filter(
                    volunteer=self.user,
                    is_active=True,
                ).exists()
                if not is_assigned:
                    raise forms.ValidationError("You can only evaluate classes where you are assigned as volunteer.")

        return cleaned_data