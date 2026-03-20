from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Language(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=10, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    flag = models.CharField(max_length=10, blank=True, default="🌍")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class AgeGroup(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    education_stage = models.CharField(max_length=100, blank=True)
    label = models.CharField(max_length=150, blank=True)
    min_age = models.PositiveIntegerField(null=True, blank=True)
    max_age = models.PositiveIntegerField(null=True, blank=True)
    display_order = models.PositiveIntegerField(default=9999)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.label or self.name


class Topic(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    name_fr = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    display_order = models.PositiveIntegerField(default=9999)
    status = models.CharField(max_length=50, blank=True, default="published")

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class CourseStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    REJECTED = "rejected", "Rejected"
    ARCHIVED = "archived", "Archived"


class Course(TimeStampedModel):
    title = models.CharField(max_length=255)
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="courses",
    )
    age_group = models.ForeignKey(
        AgeGroup,
        on_delete=models.PROTECT,
        related_name="courses",
        null=True,
        blank=True,
    )
    sessions_count = models.PositiveIntegerField(default=0)
    minutes_per_session = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    card_image = models.URLField(blank=True, max_length=1000)
    slug = models.SlugField(max_length=255, unique=True)
    display_order = models.PositiveIntegerField(default=9999)

    status = models.CharField(
        max_length=20,
        choices=CourseStatus.choices,
        default=CourseStatus.DRAFT,
        db_index=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses_created",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses_approved",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    moderation_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.status == CourseStatus.PUBLISHED


class GameDifficulty(models.TextChoices):
    EASY = "easy", "Easy"
    MEDIUM = "medium", "Medium"
    HARD = "hard", "Hard"


class Game(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    name_fr = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    description_fr = models.TextField(blank=True)
    main_image_url = models.URLField(blank=True, max_length=1000)
    duration_minutes = models.PositiveIntegerField(default=0)
    materials_needed = models.TextField(blank=True)
    variants = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    status = models.CharField(max_length=50, blank=True, default="published")

    difficulty = models.CharField(
        max_length=20,
        choices=GameDifficulty.choices,
        default=GameDifficulty.MEDIUM,
        db_index=True,
    )

    topics = models.ManyToManyField(
        Topic,
        blank=True,
        related_name="games",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CourseTopic(TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_topics",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.PROTECT,
        related_name="course_topics",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    sequence_number = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=255, unique=True)
    icon = models.CharField(max_length=100, blank=True)
    grammar_objectives = models.TextField(blank=True)
    lexical_objectives = models.TextField(blank=True)
    action_objectives = models.TextField(blank=True)
    status = models.CharField(max_length=50, blank=True, default="published")

    class Meta:
        ordering = ["course", "sequence_number", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "sequence_number"],
                name="unique_course_topic_sequence_per_course",
            ),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseTopicGame(TimeStampedModel):
    course_topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name="course_topic_games",
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.PROTECT,
        related_name="course_topic_games",
    )
    order_in_topic = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["course_topic", "order_in_topic", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["course_topic", "order_in_topic"],
                name="unique_game_order_per_course_topic",
            ),
        ]

    def __str__(self):
        return f"{self.course_topic} -> {self.game.name} ({self.order_in_topic})"


class VocabularyConcept(TimeStampedModel):
    concept_key = models.SlugField(max_length=255, unique=True)
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vocabulary_concepts",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["concept_key"]

    def __str__(self):
        return self.concept_key


class VocabularyTranslation(TimeStampedModel):
    concept = models.ForeignKey(
        VocabularyConcept,
        on_delete=models.CASCADE,
        related_name="translations",
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="vocabulary_translations",
    )
    word = models.CharField(max_length=255)
    part_of_speech = models.CharField(max_length=100, blank=True)
    phonetic = models.CharField(max_length=255, blank=True)
    audio_file = models.FileField(upload_to="pronunciations/vocabulary/", blank=True, null=True)
    flashcard_pdf = models.FileField(upload_to="flashcards/vocabulary/", blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["word"]
        constraints = [
            models.UniqueConstraint(
                fields=["concept", "language"],
                name="unique_vocabulary_translation_per_language",
            ),
        ]

    def __str__(self):
        return f"{self.word} [{self.language.code}]"


class CourseTopicVocabulary(TimeStampedModel):
    course_topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name="course_topic_vocabulary",
    )
    translation = models.ForeignKey(
        VocabularyTranslation,
        on_delete=models.CASCADE,
        related_name="course_topic_links",
    )
    order_in_topic = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["course_topic", "order_in_topic", "translation__word"]
        constraints = [
            models.UniqueConstraint(
                fields=["course_topic", "translation"],
                name="unique_vocabulary_translation_per_course_topic",
            ),
        ]

    def __str__(self):
        return f"{self.course_topic} -> {self.translation.word}"


class PhraseConcept(TimeStampedModel):
    concept_key = models.SlugField(max_length=255, unique=True)
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="phrase_concepts",
    )
    phrase_type = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["concept_key"]

    def __str__(self):
        return self.concept_key


class PhraseTranslation(TimeStampedModel):
    concept = models.ForeignKey(
        PhraseConcept,
        on_delete=models.CASCADE,
        related_name="translations",
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name="phrase_translations",
    )
    text = models.TextField()
    phonetic = models.CharField(max_length=255, blank=True)
    audio_file = models.FileField(upload_to="pronunciations/phrases/", blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["text"]
        constraints = [
            models.UniqueConstraint(
                fields=["concept", "language"],
                name="unique_phrase_translation_per_language",
            ),
        ]

    def __str__(self):
        return f"{self.text[:60]} [{self.language.code}]"


class CourseTopicPhrase(TimeStampedModel):
    course_topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name="course_topic_phrases",
    )
    translation = models.ForeignKey(
        PhraseTranslation,
        on_delete=models.CASCADE,
        related_name="course_topic_links",
    )
    order_in_topic = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["course_topic", "order_in_topic", "translation__text"]
        constraints = [
            models.UniqueConstraint(
                fields=["course_topic", "translation"],
                name="unique_phrase_translation_per_course_topic",
            ),
        ]

    def __str__(self):
        return f"{self.course_topic} -> {self.translation.text[:40]}"