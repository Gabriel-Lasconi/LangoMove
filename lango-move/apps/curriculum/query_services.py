from apps.curriculum.models import (
    Course,
    CourseStatus,
    CourseTopic,
    CourseTopicGame,
    PhraseTranslation,
    VocabularyTranslation,
)


class CurriculumQueryService:
    def get_published_courses(self):
        return (
            Course.objects
            .select_related("language", "age_group")
            .filter(status=CourseStatus.PUBLISHED)
            .order_by("display_order", "title")
        )

    def get_course_by_slug(self, slug: str):
        return (
            Course.objects
            .select_related("language", "age_group")
            .filter(status=CourseStatus.PUBLISHED, slug=slug)
            .first()
        )

    def get_course_topics_for_course(self, course):
        return (
            CourseTopic.objects
            .select_related("topic", "course")
            .filter(course=course, status="published")
            .order_by("sequence_number", "title")
        )

    def get_course_topic_by_slug(self, slug: str):
        return (
            CourseTopic.objects
            .select_related("course", "topic", "course__language", "course__age_group")
            .filter(
                status="published",
                slug=slug,
                course__status=CourseStatus.PUBLISHED,
            )
            .first()
        )

    def get_games_for_course_topic(self, course_topic):
        return (
            CourseTopicGame.objects
            .select_related("game")
            .filter(course_topic=course_topic)
            .order_by("order_in_topic", "id")
        )

    def get_all_vocabulary(self):
        return (
            VocabularyTranslation.objects
            .select_related("language", "concept", "concept__topic")
            .order_by("word")
        )

    def get_all_phrases(self):
        return (
            PhraseTranslation.objects
            .select_related("language", "concept", "concept__topic")
            .order_by("text")
        )

    def get_language_options_for_pronunciation(self):
        vocabulary_languages = (
            VocabularyTranslation.objects
            .select_related("language")
            .values_list("language__name", flat=True)
        )
        phrase_languages = (
            PhraseTranslation.objects
            .select_related("language")
            .values_list("language__name", flat=True)
        )

        return sorted({
            name.strip()
            for name in list(vocabulary_languages) + list(phrase_languages)
            if name and name.strip()
        })

    def get_pos_options_for_pronunciation(self):
        return sorted({
            value.strip()
            for value in VocabularyTranslation.objects.values_list("part_of_speech", flat=True)
            if value and value.strip()
        })

    def get_topic_options_for_pronunciation(self):
        vocabulary_topics = (
            VocabularyTranslation.objects
            .select_related("concept__topic")
            .values_list("concept__topic__name", flat=True)
        )
        phrase_topics = (
            PhraseTranslation.objects
            .select_related("concept__topic")
            .values_list("concept__topic__name", flat=True)
        )

        return sorted({
            name.strip()
            for name in list(vocabulary_topics) + list(phrase_topics)
            if name and name.strip()
        })

    def get_user_visible_courses(self, user):
        queryset = Course.objects.select_related("language", "age_group")

        if getattr(user, "is_authenticated", False) and getattr(user, "role", None) == "admin":
            return queryset.order_by("display_order", "title")

        return queryset.filter(status=CourseStatus.PUBLISHED).order_by("display_order", "title")

    def get_courses_created_by_user(self, user):
        return (
            Course.objects
            .select_related("language", "age_group", "created_by", "approved_by")
            .filter(created_by=user)
            .order_by("-created_at", "title")
        )

    def get_all_courses_for_moderation(self):
        return (
            Course.objects
            .select_related("language", "age_group", "created_by", "approved_by")
            .order_by("status", "-created_at", "title")
        )