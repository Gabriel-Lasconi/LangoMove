from django import forms
from django.forms import formset_factory
from django.utils.text import slugify

from apps.curriculum.models import AgeGroup, Course, CourseStatus, CourseTopic, Game, Language, Topic


LANGUAGE_CODE_MAP = {
    "english": "en",
    "french": "fr",
    "german": "de",
    "spanish": "es",
    "italian": "it",
    "portuguese": "pt",
    "dutch": "nl",
    "romanian": "ro",
    "russian": "ru",
    "ukrainian": "uk",
    "arabic": "ar",
    "turkish": "tr",
    "bulgarian": "bg",
    "greek": "el",
    "polish": "pl",
    "czech": "cs",
    "swedish": "sv",
    "danish": "da",
    "norwegian": "no",
    "finnish": "fi",
    "hungarian": "hu",
    "japanese": "ja",
    "chinese": "zh",
    "korean": "ko",
}


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


def get_or_create_language_from_name(language_name: str) -> Language:
    normalized_name = (language_name or "").strip()
    if not normalized_name:
        raise forms.ValidationError("Language is required.")

    existing = Language.objects.filter(name__iexact=normalized_name).first()
    if existing:
        return existing

    code = LANGUAGE_CODE_MAP.get(normalized_name.lower())
    if not code:
        raise forms.ValidationError(
            "This language is not yet supported for automatic creation. "
            "Please ask an admin to add it first."
        )

    slug = generate_unique_slug(Language, normalized_name)

    return Language.objects.create(
        name=normalized_name.title(),
        code=code,
        slug=slug,
        flag="🌍",
    )


class CourseSubmissionForm(forms.ModelForm):
    language_name = forms.CharField(
        max_length=100,
        label="Language",
        widget=forms.TextInput(attrs={"placeholder": "Type a language, e.g. English"}),
    )

    class Meta:
        model = Course
        fields = [
            "title",
            "language_name",
            "age_group",
            "sessions_count",
            "minutes_per_session",
            "description",
            "card_image",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Course title"}),
            "sessions_count": forms.NumberInput(attrs={"min": 1, "max": 50}),
            "minutes_per_session": forms.NumberInput(attrs={"min": 1}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Describe the course"}),
            "card_image": forms.URLInput(attrs={"placeholder": "Optional image URL"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.language:
            self.fields["language_name"].initial = self.instance.language.name

    def clean_language_name(self):
        value = self.cleaned_data["language_name"].strip()
        if not value:
            raise forms.ValidationError("Language is required.")
        return value

    def clean_sessions_count(self):
        value = self.cleaned_data["sessions_count"]
        if value < 1:
            raise forms.ValidationError("A course must have at least 1 session.")
        return value

    def save(self, commit=True, created_by=None):
        instance = super().save(commit=False)

        language_name = self.cleaned_data["language_name"]
        instance.language = get_or_create_language_from_name(language_name)

        if not instance.slug:
            instance.slug = generate_unique_slug(Course, instance.title, instance.pk)

        instance.status = CourseStatus.DRAFT

        if created_by and not instance.created_by:
            instance.created_by = created_by

        if commit:
            instance.save()

        return instance


class CourseModerationForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["status", "display_order", "moderation_notes"]
        widgets = {
            "moderation_notes": forms.Textarea(attrs={"rows": 4}),
        }


class CourseTopicBuilderForm(forms.Form):
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.order_by("display_order", "name"),
        required=False,
        empty_label="Choose topic",
    )
    title = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Session title"}),
    )
    grammar_objectives = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Grammar objectives"}),
    )
    lexical_objectives = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Lexical objectives"}),
    )
    action_objectives = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Action objectives"}),
    )

    game_1 = forms.ModelChoiceField(
        queryset=Game.objects.order_by("name"),
        required=True,
        empty_label="Choose game 1",
    )
    game_2 = forms.ModelChoiceField(
        queryset=Game.objects.order_by("name"),
        required=True,
        empty_label="Choose game 2",
    )
    game_3 = forms.ModelChoiceField(
        queryset=Game.objects.order_by("name"),
        required=True,
        empty_label="Choose game 3",
    )
    game_4 = forms.ModelChoiceField(
        queryset=Game.objects.order_by("name"),
        required=False,
        empty_label="Optional game 4",
    )
    game_5 = forms.ModelChoiceField(
        queryset=Game.objects.order_by("name"),
        required=False,
        empty_label="Optional game 5",
    )

    def __init__(self, *args, session_number=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_number = session_number

    def clean(self):
        cleaned_data = super().clean()
        topic = cleaned_data.get("topic")
        title = cleaned_data.get("title")

        if not topic and not title:
            raise forms.ValidationError("Each session needs at least a topic or a title.")

        selected_games = [
            cleaned_data.get("game_1"),
            cleaned_data.get("game_2"),
            cleaned_data.get("game_3"),
            cleaned_data.get("game_4"),
            cleaned_data.get("game_5"),
        ]
        selected_games = [game for game in selected_games if game]

        if len(selected_games) < 3:
            raise forms.ValidationError("Each session must contain at least 3 games.")

        if len(selected_games) > 5:
            raise forms.ValidationError("Each session can contain at most 5 games.")

        game_ids = [game.pk for game in selected_games]
        if len(game_ids) != len(set(game_ids)):
            raise forms.ValidationError("You cannot select the same game twice in one session.")

        return cleaned_data

    def get_selected_games(self):
        selected_games = [
            self.cleaned_data.get("game_1"),
            self.cleaned_data.get("game_2"),
            self.cleaned_data.get("game_3"),
            self.cleaned_data.get("game_4"),
            self.cleaned_data.get("game_5"),
        ]
        return [game for game in selected_games if game]


CourseTopicBuilderFormSet = formset_factory(
    CourseTopicBuilderForm,
    extra=0,
)