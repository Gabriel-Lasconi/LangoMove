from django.shortcuts import render

from apps.integrations.airtable.services import AirtableContentService


def pronunciation_studio_view(request):
    service = AirtableContentService()

    item_type = request.GET.get("type", "all")
    missing_only = request.GET.get("missing") == "1"

    vocabulary_items = service.get_all_vocabulary()
    phrase_items = service.get_all_phrases()

    def has_audio(item: dict) -> bool:
        audio_files = item.get("audio_file") or []
        return bool(audio_files and isinstance(audio_files, list) and audio_files[0].get("url"))

    if missing_only:
        vocabulary_items = [item for item in vocabulary_items if not has_audio(item)]
        phrase_items = [item for item in phrase_items if not has_audio(item)]

    if item_type == "vocabulary":
        phrase_items = []
    elif item_type == "phrases":
        vocabulary_items = []

    language_options = sorted(
        {
            (item.get("language_name") or item.get("language_code") or "").strip()
            for item in (vocabulary_items + phrase_items)
            if (item.get("language_name") or item.get("language_code") or "").strip()
        },
        key=lambda value: value.lower(),
    )

    pos_options = sorted(
        {
            (item.get("part_of_speech") or "").strip()
            for item in vocabulary_items
            if (item.get("part_of_speech") or "").strip()
        },
        key=lambda value: value.lower(),
    )

    topic_options = sorted(
        {
            topic.strip()
            for item in (vocabulary_items + phrase_items)
            for topic in (item.get("topic_names") or [])
            if topic and topic.strip()
        },
        key=lambda value: value.lower(),
    )

    return render(
        request,
        "website/pronunciation_studio.html",
        {
            "item_type": item_type,
            "missing_only": missing_only,
            "vocabulary_items": vocabulary_items,
            "phrase_items": phrase_items,
            "language_options": language_options,
            "pos_options": pos_options,
            "topic_options": topic_options,
        },
    )