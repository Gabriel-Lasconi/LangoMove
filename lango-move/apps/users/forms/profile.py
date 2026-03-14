from django import forms
from django.conf import settings

from apps.integrations.airtable.client import AirtableClient
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
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us a bit about yourself"}),
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
        try:
            airtable = AirtableClient()
            records = airtable.list_records(settings.AIRTABLE_TABLES["languages"])

            choices = [("", "---------")]
            seen = set()

            for record in records:
                fields = record.get("fields", {})
                name = (fields.get("name") or "").strip()

                if name and name not in seen:
                    choices.append((name, name))
                    seen.add(name)

            return choices
        except Exception:
            return [("", "---------")]

    def get_session_choices(self):
        try:
            airtable = AirtableClient()
            records = airtable.list_records(settings.AIRTABLE_TABLES["sessions"])

            sessions = []
            seen = set()

            for record in records:
                fields = record.get("fields", {})
                full_title = (fields.get("full-title") or "").strip()
                session_number = fields.get("session-number")

                if not full_title:
                    continue

                number = int(session_number) if session_number is not None else 9999
                unique_key = (number, full_title)

                if unique_key in seen:
                    continue

                seen.add(unique_key)
                sessions.append((number, full_title))

            sessions.sort(key=lambda x: x[0])

            return [("", "---------")] + [(title, title) for _, title in sessions]
        except Exception:
            return [("", "---------")]

    def get_children_group_choices(self):
        try:
            airtable = AirtableClient()
            records = airtable.list_records(settings.AIRTABLE_TABLES["age_groups"])

            groups = []
            seen = set()

            for record in records:
                fields = record.get("fields", {})
                label = (fields.get("label") or "").strip()
                display_order = fields.get("display-order")

                if not label:
                    continue

                order = int(display_order) if display_order is not None else 9999
                unique_key = (order, label)

                if unique_key in seen:
                    continue

                seen.add(unique_key)
                groups.append((order, label))

            groups.sort(key=lambda x: x[0])

            return [("", "---------")] + [(label, label) for _, label in groups]
        except Exception:
            return [("", "---------")]

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