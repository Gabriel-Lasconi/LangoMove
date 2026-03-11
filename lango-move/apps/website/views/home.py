from django.shortcuts import render
from apps.integrations.airtable.services import AirtableContentService


def home_view(request):
    service = AirtableContentService()
    courses = service.get_published_courses()

    all_age_groups = sorted(
        {course["age_group_name"] for course in courses if course.get("age_group_name")}
    )
    all_languages = sorted(
        {course["language_name"] for course in courses if course.get("language_name")}
    )

    return render(
        request,
        "website/home.html",
        {
            "courses": courses,
            "all_age_groups": all_age_groups,
            "all_languages": all_languages,
        },
    )