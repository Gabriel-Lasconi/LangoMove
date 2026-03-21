from django import forms
from django.forms import formset_factory
from django.utils.text import slugify
from django import forms
from apps.curriculum.models import Game, Topic

from apps.curriculum.models import AgeGroup, Course, CourseStatus, CourseTopic, Game, Language, Topic


LANGUAGE_METADATA = {
    "english": {"code": "en", "flag": "🇬🇧"},
    "mandarin": {"code": "zh", "flag": "🇨🇳"},
    "chinese": {"code": "zh", "flag": "🇨🇳"},
    "hindi": {"code": "hi", "flag": "🇮🇳"},
    "spanish": {"code": "es", "flag": "🇪🇸"},
    "french": {"code": "fr", "flag": "🇫🇷"},
    "arabic": {"code": "ar", "flag": "🇸🇦"},
    "bengali": {"code": "bn", "flag": "🇧🇩"},
    "portuguese": {"code": "pt", "flag": "🇵🇹"},
    "russian": {"code": "ru", "flag": "🇷🇺"},
    "urdu": {"code": "ur", "flag": "🇵🇰"},
    "indonesian": {"code": "id", "flag": "🇮🇩"},
    "german": {"code": "de", "flag": "🇩🇪"},
    "japanese": {"code": "ja", "flag": "🇯🇵"},
    "swahili": {"code": "sw", "flag": "🇹🇿"},
    "marathi": {"code": "mr", "flag": "🇮🇳"},
    "telugu": {"code": "te", "flag": "🇮🇳"},
    "turkish": {"code": "tr", "flag": "🇹🇷"},
    "tamil": {"code": "ta", "flag": "🇮🇳"},
    "korean": {"code": "ko", "flag": "🇰🇷"},
    "vietnamese": {"code": "vi", "flag": "🇻🇳"},
    "italian": {"code": "it", "flag": "🇮🇹"},
    "persian": {"code": "fa", "flag": "🇮🇷"},
    "farsi": {"code": "fa", "flag": "🇮🇷"},
    "polish": {"code": "pl", "flag": "🇵🇱"},
    "dutch": {"code": "nl", "flag": "🇳🇱"},
    "romanian": {"code": "ro", "flag": "🇷🇴"},
    "greek": {"code": "el", "flag": "🇬🇷"},
    "ukrainian": {"code": "uk", "flag": "🇺🇦"},
    "czech": {"code": "cs", "flag": "🇨🇿"},
    "swedish": {"code": "sv", "flag": "🇸🇪"},
    "danish": {"code": "da", "flag": "🇩🇰"},
    "norwegian": {"code": "no", "flag": "🇳🇴"},
    "finnish": {"code": "fi", "flag": "🇫🇮"},
    "hungarian": {"code": "hu", "flag": "🇭🇺"},
    "bulgarian": {"code": "bg", "flag": "🇧🇬"},
}


AGE_GROUP_CODE_MAP = {
    "cp": "CP",
    "gs": "GS",
    "grande section": "GS",
    "petite section": "PS",
    "moyenne section": "MS",
    "ce1": "CE1",
    "ce2": "CE2",
    "cm1": "CM1",
    "cm2": "CM2",
    "6eme": "6E",
    "6ème": "6E",
    "5eme": "5E",
    "5ème": "5E",
    "4eme": "4E",
    "4ème": "4E",
    "3eme": "3E",
    "3ème": "3E",
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

    metadata = LANGUAGE_METADATA.get(normalized_name.lower())
    if not metadata:
        raise forms.ValidationError(
            "This language is not yet supported for automatic creation. "
            "Please ask an admin to add it first."
        )

    slug = generate_unique_slug(Language, normalized_name)

    return Language.objects.create(
        name=normalized_name.title(),
        code=metadata["code"],
        slug=slug,
        flag=metadata["flag"],
    )


def get_age_group_code(age_group: AgeGroup | None) -> str:
    if not age_group:
        return "AGE"

    candidates = [
        (age_group.name or "").strip(),
        (age_group.label or "").strip(),
        (age_group.education_stage or "").strip(),
    ]

    for candidate in candidates:
        lowered = candidate.lower()
        if lowered in AGE_GROUP_CODE_MAP:
            return AGE_GROUP_CODE_MAP[lowered]

    raw = (age_group.name or age_group.label or "").strip().upper()
    if raw:
        compact = raw.replace(" ", "").replace("-", "")
        if len(compact) <= 4:
            return compact

        words = raw.replace("-", " ").split()
        if len(words) >= 2:
            initials = "".join(word[0] for word in words[:3])
            return initials[:4]

        return compact[:4]

    return "AGE"


def build_course_title(language: Language, age_group: AgeGroup | None, sessions_count: int, minutes_per_session: int) -> str:
    language_code = (language.code or "xx").upper()
    age_group_code = get_age_group_code(age_group)
    return f"{language_code}-{age_group_code}-{sessions_count}-{minutes_per_session}"


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
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Generated automatically",
                    "readonly": "readonly",
                }
            ),
            "sessions_count": forms.NumberInput(attrs={"min": 1, "max": 30}),
            "minutes_per_session": forms.NumberInput(attrs={"min": 1, "max": 90}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Describe the course"}),
            "card_image": forms.URLInput(attrs={"placeholder": "Optional image URL"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.language:
            self.fields["language_name"].initial = self.instance.language.name

        self.fields["title"].help_text = "This title is generated automatically from language, age group, sessions, and minutes."

        for age_group in self.fields["age_group"].queryset:
            code = get_age_group_code(age_group)
            age_group.display_label = f"{age_group} ({code})"

        self.fields["age_group"].label_from_instance = lambda obj: getattr(obj, "display_label", str(obj))

    def clean_language_name(self):
        value = self.cleaned_data["language_name"].strip()
        if not value:
            raise forms.ValidationError("Language is required.")
        return value

    def clean_sessions_count(self):
        value = self.cleaned_data["sessions_count"]
        if value < 1:
            raise forms.ValidationError("A course must have at least 1 session.")
        if value > 30:
            raise forms.ValidationError("A course cannot have more than 30 sessions.")
        return value

    def clean_minutes_per_session(self):
        value = self.cleaned_data["minutes_per_session"]
        if value < 1:
            raise forms.ValidationError("Minutes per session must be at least 1.")
        if value > 90:
            raise forms.ValidationError("Minutes per session cannot be more than 90.")
        return value

    def clean(self):
        cleaned_data = super().clean()

        language_name = cleaned_data.get("language_name")
        age_group = cleaned_data.get("age_group")
        sessions_count = cleaned_data.get("sessions_count")
        minutes_per_session = cleaned_data.get("minutes_per_session")

        if language_name and sessions_count and minutes_per_session:
            language = get_or_create_language_from_name(language_name)
            cleaned_data["resolved_language"] = language
            cleaned_data["title"] = build_course_title(
                language=language,
                age_group=age_group,
                sessions_count=sessions_count,
                minutes_per_session=minutes_per_session,
            )

        return cleaned_data

    def save(self, commit=True, created_by=None):
        instance = super().save(commit=False)

        language = self.cleaned_data.get("resolved_language")
        if not language:
            language_name = self.cleaned_data["language_name"]
            language = get_or_create_language_from_name(language_name)

        instance.language = language

        instance.title = build_course_title(
            language=language,
            age_group=self.cleaned_data.get("age_group"),
            sessions_count=self.cleaned_data["sessions_count"],
            minutes_per_session=self.cleaned_data["minutes_per_session"],
        )

        if not instance.slug or instance.slug != slugify(instance.title):
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
        widget=forms.TextInput(
            attrs={
                "placeholder": "Generated automatically",
                "readonly": "readonly",
            }
        ),
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
        self.fields["title"].help_text = "Generated automatically from the session number and topic."

        initial_topic = None
        topic_value = self.data.get(self.add_prefix("topic")) or self.initial.get("topic")

        if topic_value:
            try:
                initial_topic = Topic.objects.filter(pk=topic_value).first()
            except (ValueError, TypeError):
                initial_topic = None

        if not self.initial.get("title"):
            self.initial["title"] = self.build_session_title(initial_topic)

    def build_session_title(self, topic=None):
        base = f"Session {self.session_number}" if self.session_number else "Session"
        if topic and getattr(topic, "name", None):
            return f"{base} - {topic.name}"
        return base

    def clean(self):
        cleaned_data = super().clean()
        topic = cleaned_data.get("topic")

        if not topic:
            raise forms.ValidationError("Each session needs a topic so the title can be generated automatically.")

        cleaned_data["title"] = self.build_session_title(topic)

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

class GameAdminForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.order_by("display_order", "name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Game
        fields = [
            "name",
            "name_fr",
            "description",
            "description_fr",
            "main_image_url",
            "duration_minutes",
            "difficulty",
            "materials_needed",
            "variants",
            "topics",
            "status",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Game name"}),
            "name_fr": forms.TextInput(attrs={"placeholder": "French game name"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Description"}),
            "description_fr": forms.Textarea(attrs={"rows": 4, "placeholder": "French description"}),
            "main_image_url": forms.URLInput(attrs={"placeholder": "Image URL"}),
            "duration_minutes": forms.NumberInput(attrs={"min": 0, "max": 180}),
            "materials_needed": forms.Textarea(attrs={"rows": 4, "placeholder": "Materials needed"}),
            "variants": forms.Textarea(attrs={"rows": 5, "placeholder": "Variants"}),
            "status": forms.TextInput(attrs={"placeholder": "published"}),
        }