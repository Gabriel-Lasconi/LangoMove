from django.urls import path

from apps.website.views import (
    course_build_sessions_view,
    course_create_view,
    course_detail_view,
    course_edit_view,
    course_moderation_detail_view,
    course_moderation_list_view,
    course_submission_list_view,
    game_detail_json_view,
    home_view,
    pronunciation_studio_view,
    session_detail_view,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("courses/<slug:slug>/", course_detail_view, name="course-detail"),
    path("sessions/<slug:slug>/", session_detail_view, name="session-detail"),
    path("api/games/<slug:slug>/", game_detail_json_view, name="game-detail-json"),
    path("pronunciation-studio/", pronunciation_studio_view, name="pronunciation-studio"),

    path("course-submissions/", course_submission_list_view, name="course-submission-list"),
    path("course-submissions/new/", course_create_view, name="course-create"),
    path("course-submissions/<int:pk>/edit/", course_edit_view, name="course-edit"),
    path("course-submissions/<int:pk>/sessions/", course_build_sessions_view, name="course-build-sessions"),

    path("moderation/courses/", course_moderation_list_view, name="course-moderation-list"),
    path("moderation/courses/<int:pk>/", course_moderation_detail_view, name="course-moderation-detail"),
]