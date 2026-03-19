from django import forms

from apps.curriculum.models import Course, CourseTopic, Topic
from apps.schools.models import ClassTopicEvaluation, Classroom
from apps.users.models import UserRole


class ClassTopicEvaluationForm(forms.ModelForm):
    classroom = forms.ModelChoiceField(
        queryset=Classroom.objects.none(),
        required=True,
        empty_label="---------",
    )
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.order_by("name"),
        required=True,
        empty_label="---------",
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        required=False,
        empty_label="---------",
    )
    course_topic = forms.ModelChoiceField(
        queryset=CourseTopic.objects.none(),
        required=False,
        empty_label="---------",
    )

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
            "strengths": forms.Textarea(attrs={"rows": 4, "placeholder": "Strengths observed"}),
            "weaknesses": forms.Textarea(attrs={"rows": 4, "placeholder": "Weaknesses observed"}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Additional notes"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        allowed_classrooms = self.get_allowed_classrooms()
        self.fields["classroom"].queryset = allowed_classrooms

        selected_classroom = None
        classroom_value = self.data.get("classroom") or self.initial.get("classroom")

        if classroom_value:
            try:
                selected_classroom = allowed_classrooms.get(pk=classroom_value)
            except (Classroom.DoesNotExist, ValueError, TypeError):
                selected_classroom = None
        elif self.instance and self.instance.pk and self.instance.classroom_id:
            selected_classroom = self.instance.classroom

        if selected_classroom and selected_classroom.course:
            self.fields["course"].queryset = Course.objects.filter(pk=selected_classroom.course_id)
            self.fields["course"].initial = selected_classroom.course
            self.fields["course"].widget.attrs["readonly"] = True
            self.fields["course"].widget.attrs["disabled"] = True

            self.fields["course_topic"].queryset = (
                CourseTopic.objects
                .filter(course=selected_classroom.course)
                .order_by("sequence_number", "title")
            )
        else:
            self.fields["course"].queryset = Course.objects.none()
            self.fields["course_topic"].queryset = CourseTopic.objects.none()

    def get_allowed_classrooms(self):
        if not self.user:
            return Classroom.objects.none()

        if self.user.role == UserRole.ADMIN:
            return (
                Classroom.objects
                .select_related("school", "teacher", "course", "age_group")
                .order_by("school__name", "name")
            )

        if self.user.role == UserRole.TEACHER:
            return (
                Classroom.objects
                .filter(teacher=self.user)
                .select_related("school", "teacher", "course", "age_group")
                .order_by("school__name", "name")
            )

        if self.user.role == UserRole.VOLUNTEER:
            return (
                Classroom.objects
                .filter(
                    volunteer_assignments__volunteer=self.user,
                    volunteer_assignments__is_active=True,
                )
                .select_related("school", "teacher", "course", "age_group")
                .distinct()
                .order_by("school__name", "name")
            )

        return Classroom.objects.none()

    def clean_classroom(self):
        classroom = self.cleaned_data["classroom"]
        allowed_ids = set(self.get_allowed_classrooms().values_list("id", flat=True))

        if classroom.id not in allowed_ids:
            raise forms.ValidationError("You are not allowed to evaluate this classroom.")

        return classroom

    def clean(self):
        cleaned_data = super().clean()
        classroom = cleaned_data.get("classroom")
        course_topic = cleaned_data.get("course_topic")

        if classroom and classroom.course:
            cleaned_data["course"] = classroom.course

            if course_topic and course_topic.course_id != classroom.course_id:
                self.add_error(
                    "course_topic",
                    "Selected course topic does not belong to the classroom course.",
                )
        elif course_topic:
            self.add_error(
                "course_topic",
                "You cannot select a course topic without a classroom course.",
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.user:
            instance.evaluated_by = self.user

        if instance.classroom and instance.classroom.course:
            instance.course = instance.classroom.course

        if commit:
            instance.save()

        return instance