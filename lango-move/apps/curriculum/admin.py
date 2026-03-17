from django.contrib import admin

from .models import (
    AgeGroup,
    Course,
    CourseTopic,
    CourseTopicGame,
    CourseTopicPhrase,
    CourseTopicVocabulary,
    Game,
    Language,
    PhraseConcept,
    PhraseTranslation,
    Topic,
    VocabularyConcept,
    VocabularyTranslation,
)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "slug", "created_at", "updated_at")
    search_fields = ("name", "code", "slug")
    ordering = ("name",)


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "name",
        "education_stage",
        "min_age",
        "max_age",
        "display_order",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "label", "education_stage")
    ordering = ("display_order", "name")


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "name_fr",
        "slug",
        "display_order",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "name_fr", "slug")
    list_filter = ("status",)
    ordering = ("display_order", "name")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "language",
        "age_group",
        "minutes_per_session",
        "display_order",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "slug", "description")
    list_filter = ("language", "age_group", "status")
    ordering = ("display_order", "title")
    autocomplete_fields = ("language", "age_group")


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "duration_minutes",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "name_fr", "slug", "description", "description_fr")
    list_filter = ("status",)
    ordering = ("name",)


class CourseTopicGameInline(admin.TabularInline):
    model = CourseTopicGame
    extra = 0
    autocomplete_fields = ("game",)
    ordering = ("order_in_topic", "id")


class CourseTopicVocabularyInline(admin.TabularInline):
    model = CourseTopicVocabulary
    extra = 0
    autocomplete_fields = ("translation",)
    ordering = ("order_in_topic", "id")


class CourseTopicPhraseInline(admin.TabularInline):
    model = CourseTopicPhrase
    extra = 0
    autocomplete_fields = ("translation",)
    ordering = ("order_in_topic", "id")


@admin.register(CourseTopic)
class CourseTopicAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "topic",
        "sequence_number",
        "slug",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "slug", "course__title", "topic__name")
    list_filter = ("course", "topic", "status")
    ordering = ("course", "sequence_number", "title")
    autocomplete_fields = ("course", "topic")
    inlines = [
        CourseTopicGameInline,
        CourseTopicVocabularyInline,
        CourseTopicPhraseInline,
    ]


@admin.register(CourseTopicGame)
class CourseTopicGameAdmin(admin.ModelAdmin):
    list_display = ("course_topic", "game", "order_in_topic", "created_at", "updated_at")
    search_fields = ("course_topic__title", "game__name")
    list_filter = ("course_topic__course",)
    ordering = ("course_topic", "order_in_topic")
    autocomplete_fields = ("course_topic", "game")


@admin.register(VocabularyConcept)
class VocabularyConceptAdmin(admin.ModelAdmin):
    list_display = ("concept_key", "topic", "created_at", "updated_at")
    search_fields = ("concept_key", "notes")
    list_filter = ("topic",)
    ordering = ("concept_key",)
    autocomplete_fields = ("topic",)


@admin.register(VocabularyTranslation)
class VocabularyTranslationAdmin(admin.ModelAdmin):
    list_display = (
        "word",
        "language",
        "concept",
        "part_of_speech",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "word",
        "phonetic",
        "notes",
        "concept__concept_key",
        "language__name",
        "language__code",
    )
    list_filter = ("language", "part_of_speech")
    ordering = ("word",)
    autocomplete_fields = ("concept", "language")


@admin.register(CourseTopicVocabulary)
class CourseTopicVocabularyAdmin(admin.ModelAdmin):
    list_display = ("course_topic", "translation", "order_in_topic", "created_at", "updated_at")
    search_fields = ("course_topic__title", "translation__word")
    list_filter = ("course_topic__course", "translation__language")
    ordering = ("course_topic", "order_in_topic")
    autocomplete_fields = ("course_topic", "translation")


@admin.register(PhraseConcept)
class PhraseConceptAdmin(admin.ModelAdmin):
    list_display = ("concept_key", "topic", "phrase_type", "created_at", "updated_at")
    search_fields = ("concept_key", "notes")
    list_filter = ("topic", "phrase_type")
    ordering = ("concept_key",)
    autocomplete_fields = ("topic",)


@admin.register(PhraseTranslation)
class PhraseTranslationAdmin(admin.ModelAdmin):
    list_display = (
        "short_text",
        "language",
        "concept",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "text",
        "phonetic",
        "notes",
        "concept__concept_key",
        "language__name",
        "language__code",
    )
    list_filter = ("language",)
    ordering = ("text",)
    autocomplete_fields = ("concept", "language")

    @admin.display(description="Text")
    def short_text(self, obj):
        return obj.text[:80]


@admin.register(CourseTopicPhrase)
class CourseTopicPhraseAdmin(admin.ModelAdmin):
    list_display = ("course_topic", "translation", "order_in_topic", "created_at", "updated_at")
    search_fields = ("course_topic__title", "translation__text")
    list_filter = ("course_topic__course", "translation__language")
    ordering = ("course_topic", "order_in_topic")
    autocomplete_fields = ("course_topic", "translation")