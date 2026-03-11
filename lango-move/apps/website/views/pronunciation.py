from django.shortcuts import render
from apps.integrations.airtable.services import AirtableContentService


def pronunciation_studio_view(request):
    service = AirtableContentService()

    vocabulary_items = service.get_all_vocabulary()
    phrase_items = service.get_all_phrases()

    missing_only = request.GET.get("missing") == "1"
    item_type = request.GET.get("type", "all")

    if missing_only:
        vocabulary_items = [item for item in vocabulary_items if not item.get("audio_url")]
        phrase_items = [item for item in phrase_items if not item.get("audio_url")]

    if item_type == "vocabulary":
        phrase_items = []
    elif item_type == "phrases":
        vocabulary_items = []

    return render(
        request,
        "website/pronunciation_studio.html",
        {
            "vocabulary_items": vocabulary_items,
            "phrase_items": phrase_items,
            "missing_only": missing_only,
            "item_type": item_type,
        },
    )