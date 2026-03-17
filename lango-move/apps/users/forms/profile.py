from django import forms

from apps.curriculum.models import AgeGroup, CourseTopic, Language
from apps.users.models import ClassParticipation, User, UserRole


class UserAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "photo",
            "date_of_birth",
            "phone",
            "city",
            "country",
            "bio",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "country": forms.TextInput(attrs={"placeholder": "Country"}),
            "bio": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Tell us a bit about yourself"}
            ),
        }


class ClassParticipationForm(forms.ModelForm):
    language = forms.ChoiceField(choices=[], required=True)
    session_title = forms.ChoiceField(choices=[], required=False)
    children_group = forms.ChoiceField(choices=[], required=False)

    class Meta:
        model = ClassParticipation
        fields = [
            "date",
            "school_name",
            "children_group",
            "language",
            "session_title",
            "teacher",
            "volunteers",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "school_name": forms.TextInput(attrs={"placeholder": "School name"}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Notes"}),
            "volunteers": forms.SelectMultiple(attrs={"size": 8}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        allowed_users = User.objects.filter(
            role__in=[UserRole.VOLUNTEER, UserRole.TEACHER, UserRole.ADMIN]
        ).order_by("username")

        self.fields["teacher"].queryset = allowed_users.filter(
            role=UserRole.TEACHER
        ).order_by("username")
        self.fields["teacher"].required = False

        self.fields["volunteers"].queryset = allowed_users.filter(
            role=UserRole.VOLUNTEER
        ).order_by("username")
        self.fields["volunteers"].required = False

        self.fields["language"].choices = self.get_language_choices()
        self.fields["session_title"].choices = self.get_session_choices()
        self.fields["children_group"].choices = self.get_children_group_choices()

    def get_language_choices(self):
        languages = Language.objects.order_by("name")
        return [
            ("", "---------"),
            *[(language.name, language.name) for language in languages],
        ]

    def get_session_choices(self):
        course_topics = (
            CourseTopic.objects.select_related("course")
            .order_by("course__title", "sequence_number", "title")
        )

        seen = set()
        choices = [("", "---------")]

        for topic in course_topics:
            label = topic.title.strip() if topic.title else ""
            if not label or label in seen:
                continue
            seen.add(label)
            choices.append((label, label))

        return choices

    def get_children_group_choices(self):
        groups = AgeGroup.objects.order_by("display_order", "name")
        return [
            ("", "---------"),
            *[
                (group.label or group.name, group.label or group.name)
                for group in groups
            ],
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.user and self.user.role == UserRole.TEACHER and not instance.teacher:
            instance.teacher = self.user

        if commit:
            instance.save()
            self.save_m2m()

            if self.user and self.user.role in [UserRole.VOLUNTEER, UserRole.ADMIN]:
                instance.volunteers.add(self.user)

        return instance