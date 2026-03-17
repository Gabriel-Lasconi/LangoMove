from django.urls import path

from apps.website.views import (
    course_detail_view,
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
]