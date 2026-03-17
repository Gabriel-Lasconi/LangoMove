from django.http import Http404, JsonResponse
from django.shortcuts import render

from apps.curriculum.models import (
    CourseTopicPhrase,
    CourseTopicVocabulary,
    Game,
)
from apps.curriculum.query_services import CurriculumQueryService


def course_detail_view(request, slug):
    service = CurriculumQueryService()
    course = service.get_course_by_slug(slug)

    if not course:
        raise Http404("Course not found.")

    course_topics = service.get_course_topics_for_course(course)

    sessions = []
    for topic in course_topics:
        sessions.append({
            "id": topic.id,
            "session_id": topic.id,
            "session_number": topic.sequence_number,
            "title": topic.title,
            "full_title": topic.title,
            "slug": topic.slug,
            "topic_name": topic.topic.name if topic.topic else "",
            "grammar_objectives": topic.grammar_objectives,
            "action_objectives": topic.action_objectives,
            "lexical_objectives": topic.lexical_objectives,
            "teacher_notes": "",
        })

    course_payload = {
        "id": course.id,
        "title": course.title,
        "slug": course.slug,
        "description": course.description,
        "sessions_count": course.course_topics.count(),
        "minutes_per_session": course.minutes_per_session,
        "language_name": course.language.name if course.language else "",
        "language_flag": course.language.flag if course.language else "",
        "age_group_name": (course.age_group.label or course.age_group.name) if course.age_group else "",
        "display_order": course.display_order,
    }

    return render(
        request,
        "website/course_detail.html",
        {
            "course": course_payload,
            "sessions": sessions,
        },
    )


def session_detail_view(request, slug):
    service = CurriculumQueryService()
    course_topic = service.get_course_topic_by_slug(slug)

    if not course_topic:
        raise Http404("Session not found.")

    game_links = service.get_games_for_course_topic(course_topic)

    session_payload = {
        "id": course_topic.id,
        "session_id": course_topic.id,
        "session_number": course_topic.sequence_number,
        "title": course_topic.title,
        "full_title": course_topic.title,
        "slug": course_topic.slug,
        "grammar_objectives": course_topic.grammar_objectives,
        "action_objectives": course_topic.action_objectives,
        "lexical_objectives": course_topic.lexical_objectives,
        "teacher_notes": "",
        "course_ids": [course_topic.course.id] if course_topic.course else [],
    }

    session_games = []
    for link in game_links:
        game = link.game
        session_games.append({
            "id": link.id,
            "order_in_session": link.order_in_topic,
            "stage_name": "",
            "duration_minutes": game.duration_minutes if game else 0,
            "notes": "",
            "game_name": game.name if game else "",
            "game_name_fr": game.name_fr if game else "",
            "game_slug": game.slug if game else "",
            "game_description": game.description if game else "",
            "game_description_fr": game.description_fr if game else "",
            "game_variants": game.variants if game else "",
            "vocabulary_tags": [],
        })

    return render(
        request,
        "website/session_detail.html",
        {
            "session": session_payload,
            "session_games": session_games,
        },
    )


def game_detail_json_view(request, slug):
    game = Game.objects.filter(slug=slug).first()

    if not game:
        return JsonResponse({"error": "Game not found."}, status=404)

    course_topic_links = (
        game.course_topic_games
        .select_related("course_topic", "course_topic__topic", "course_topic__course")
        .all()
    )

    course_topic_ids = [link.course_topic_id for link in course_topic_links]

    vocabulary_links = (
        CourseTopicVocabulary.objects
        .filter(course_topic_id__in=course_topic_ids)
        .select_related(
            "translation",
            "translation__language",
            "translation__concept",
            "translation__concept__topic",
        )
        .order_by("order_in_topic", "translation__word")
    )

    phrase_links = (
        CourseTopicPhrase.objects
        .filter(course_topic_id__in=course_topic_ids)
        .select_related(
            "translation",
            "translation__language",
            "translation__concept",
            "translation__concept__topic",
        )
        .order_by("order_in_topic", "translation__text")
    )

    vocabulary = []
    seen_vocabulary_ids = set()

    for link in vocabulary_links:
        translation = link.translation
        if not translation or translation.id in seen_vocabulary_ids:
            continue

        seen_vocabulary_ids.add(translation.id)

        vocabulary.append({
            "id": translation.id,
            "word": translation.word,
            "word_fr": "",
            "importance": "",
            "category": translation.concept.topic.name if translation.concept and translation.concept.topic else "",
            "part_of_speech": translation.part_of_speech or "",
            "audio_status": "ready" if translation.audio_file else "missing",
            "phonetic": translation.phonetic or "",
            "notes": translation.notes or "",
            "audio_file": [{"url": translation.audio_file.url}] if translation.audio_file else [],
            "flashcard_pdf": [],
        })

    phrases = []
    seen_phrase_ids = set()

    for link in phrase_links:
        translation = link.translation
        if not translation or translation.id in seen_phrase_ids:
            continue

        seen_phrase_ids.add(translation.id)

        phrases.append({
            "id": translation.id,
            "text": translation.text,
            "text_fr": "",
            "importance": "",
            "phrase_type": translation.concept.phrase_type if translation.concept else "",
            "audio_status": "ready" if translation.audio_file else "missing",
            "phonetic": translation.phonetic or "",
            "notes": translation.notes or "",
            "audio_file": [{"url": translation.audio_file.url}] if translation.audio_file else [],
        })

    game_payload = {
        "id": game.id,
        "name": game.name,
        "name_fr": game.name_fr or "",
        "duration_minutes": game.duration_minutes,
        "description": game.description or "",
        "description_fr": game.description_fr or "",
        "activity_type": "",
        "materials_needed": game.materials_needed or "",
        "variants": game.variants or "",
        "notes_for_facilitator": "",
        "main_image_url": game.main_image_url or "",
        "topics": sorted({
            link.course_topic.topic.name
            for link in course_topic_links
            if link.course_topic and link.course_topic.topic
        }),
    }

    return JsonResponse({
        "game": game_payload,
        "vocabulary": vocabulary,
        "phrases": phrases,
    })