import re
from typing import Iterable

from django.utils.text import slugify

from apps.curriculum.models import AgeGroup, Course, Game, Language, Topic


def split_source_value(value) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]

    text = str(value).strip()
    if not text:
        return []

    if "," in text:
        return [part.strip() for part in text.split(",") if part.strip()]

    return [text]


def first_non_empty(values: Iterable[str]) -> str:
    for value in values:
        if value and str(value).strip():
            return str(value).strip()
    return ""


def safe_int(value, default=0):
    try:
        if value in (None, ""):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_slug(value: str, fallback: str = "item") -> str:
    result = slugify(str(value or "").strip())
    return result or fallback


def attachment_url(value) -> str:
    if not value:
        return ""

    if isinstance(value, list):
        first = value[0] if value else None
        if isinstance(first, dict):
            return (
                first.get("url")
                or first.get("download_url")
                or first.get("signedUrl")
                or ""
            )
        if isinstance(first, str):
            return first.strip()

    text = str(value).strip()

    if text.startswith("http://") or text.startswith("https://"):
        return text

    match = re.search(r"\((https?://[^\)]+)\)", text)
    if match:
        return match.group(1).strip()

    return ""


def resolve_language(value) -> Language | None:
    candidates = split_source_value(value)

    for candidate in candidates:
        obj = Language.objects.filter(code__iexact=candidate).first()
        if obj:
            return obj

        obj = Language.objects.filter(name__iexact=candidate).first()
        if obj:
            return obj

        obj = Language.objects.filter(slug=candidate).first()
        if obj:
            return obj

    return None


def resolve_age_group(value) -> AgeGroup | None:
    candidates = split_source_value(value)

    for candidate in candidates:
        obj = AgeGroup.objects.filter(name__iexact=candidate).first()
        if obj:
            return obj

        obj = AgeGroup.objects.filter(label__iexact=candidate).first()
        if obj:
            return obj

    return None


def resolve_topic(value) -> Topic | None:
    candidates = split_source_value(value)

    for candidate in candidates:
        obj = Topic.objects.filter(name__iexact=candidate).first()
        if obj:
            return obj

        obj = Topic.objects.filter(slug=candidate).first()
        if obj:
            return obj

    return None


def resolve_course(value) -> Course | None:
    candidates = split_source_value(value)

    for candidate in candidates:
        obj = Course.objects.filter(title__iexact=candidate).first()
        if obj:
            return obj

        obj = Course.objects.filter(slug=candidate).first()
        if obj:
            return obj

    return None


def resolve_game(value) -> Game | None:
    candidates = split_source_value(value)

    for candidate in candidates:
        obj = Game.objects.filter(name__iexact=candidate).first()
        if obj:
            return obj

        obj = Game.objects.filter(slug=candidate).first()
        if obj:
            return obj

    return None


def make_vocabulary_concept_key(topic_name: str, word: str) -> str:
    return safe_slug(f"{topic_name or 'general'}-{word or 'word'}", fallback="vocab-concept")


def make_phrase_concept_key(text: str) -> str:
    return safe_slug((text or "")[:80], fallback="phrase-concept")