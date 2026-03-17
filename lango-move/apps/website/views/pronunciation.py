from django.shortcuts import render

from apps.curriculum.query_services import CurriculumQueryService


def pronunciation_studio_view(request):
    service = CurriculumQueryService()

    vocabulary_queryset = service.get_all_vocabulary()
    phrase_queryset = service.get_all_phrases()

    vocabulary_items = []
    for item in vocabulary_queryset:
        vocabulary_items.append({
            "id": item.id,
            "word": item.word,
            "word_fr": "",
            "category": item.concept.topic.name if item.concept and item.concept.topic else "",
            "part_of_speech": item.part_of_speech,
            "phonetic": item.phonetic,
            "audio_file": item.audio_file,
            "language_code": item.language.code if item.language else "",
            "language_name": item.language.name if item.language else "",
            "topic_names": [item.concept.topic.name] if item.concept and item.concept.topic else [],
        })

    phrase_items = []
    for item in phrase_queryset:
        phrase_items.append({
            "id": item.id,
            "text": item.text,
            "text_fr": "",
            "phrase_type": item.concept.phrase_type if item.concept else "",
            "phonetic": item.phonetic,
            "audio_file": item.audio_file,
            "language_code": item.language.code if item.language else "",
            "language_name": item.language.name if item.language else "",
            "topic_names": [item.concept.topic.name] if item.concept and item.concept.topic else [],
        })

    context = {
        "vocabulary_items": vocabulary_items,
        "phrase_items": phrase_items,
        "language_options": service.get_language_options_for_pronunciation(),
        "pos_options": service.get_pos_options_for_pronunciation(),
        "topic_options": service.get_topic_options_for_pronunciation(),
    }

    return render(request, "website/pronunciation_studio.html", context)