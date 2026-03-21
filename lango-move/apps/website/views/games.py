from django.shortcuts import render

from apps.curriculum.query_services import CurriculumQueryService
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.curriculum.forms import GameAdminForm
from apps.curriculum.models import Game
from apps.curriculum.query_services import CurriculumQueryService


def games_studio_view(request):
    service = CurriculumQueryService()

    games = service.get_all_games()
    difficulty_options = service.get_game_difficulty_options()
    topic_options = service.get_game_topic_options()

    game_cards = []
    for game in games:
        game_cards.append({
            "id": game.id,
            "name": game.name,
            "name_fr": game.name_fr,
            "description": game.description,
            "description_fr": game.description_fr,
            "slug": game.slug,
            "status": game.status,
            "difficulty": game.difficulty,
            "difficulty_label": game.get_difficulty_display(),
            "duration_minutes": game.duration_minutes,
            "materials_needed": game.materials_needed,
            "variants": game.variants,
            "main_image_url": game.main_image_url,
            "topics": [topic.name for topic in game.topics.all()],
        })

    return render(
        request,
        "website/games_studio.html",
        {
            "games": game_cards,
            "difficulty_options": difficulty_options,
            "topic_options": topic_options,
        },
    )

@staff_member_required
def edit_game_view(request, slug):
    game = get_object_or_404(Game, slug=slug)

    if request.method == "POST":
        form = GameAdminForm(request.POST, instance=game)
        if form.is_valid():
            form.save()
            messages.success(request, f'Game "{game.name}" updated successfully.')
            return redirect("games-studio")
    else:
        form = GameAdminForm(instance=game)

    return render(
        request,
        "website/edit_game.html",
        {
            "form": form,
            "game": game,
        },
    )
