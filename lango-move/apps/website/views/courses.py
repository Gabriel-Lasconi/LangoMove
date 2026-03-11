from django.http import Http404, JsonResponse
from django.shortcuts import render
from apps.integrations.airtable.services import AirtableContentService


def course_detail_view(request, slug: str):
    service = AirtableContentService()
    course = service.get_course_by_slug(slug)

    if not course:
        raise Http404("Course not found.")

    sessions = service.get_sessions_for_course(course["airtable_id"])

    return render(
        request,
        "website/course_detail.html",
        {
            "course": course,
            "sessions": sessions,
        },
    )


def session_detail_view(request, slug: str):
    service = AirtableContentService()
    session = service.get_session_by_slug(slug)

    if not session:
        raise Http404("Session not found.")

    session_games = service.get_games_for_session(session["airtable_id"])

    return render(
        request,
        "website/session_detail.html",
        {
            "session": session,
            "session_games": session_games,
        },
    )


def game_detail_json_view(request, slug: str):
    service = AirtableContentService()
    payload = service.get_game_detail_payload(slug)

    if not payload:
        raise Http404("Game not found.")

    return JsonResponse(payload)