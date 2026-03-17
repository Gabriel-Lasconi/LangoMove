from django.shortcuts import render

from apps.curriculum.query_services import CurriculumQueryService


def home_view(request):
    service = CurriculumQueryService()
    courses_queryset = service.get_published_courses()

    courses = []
    all_age_groups = set()
    all_languages = set()

    for course in courses_queryset:
        language_name = course.language.name if course.language else ""
        language_flag = course.language.flag if course.language else ""
        age_group_name = ""

        if course.age_group:
            age_group_name = course.age_group.label or course.age_group.name

        sessions_count = course.course_topics.count()

        display_title = course.title

        courses.append({
            "id": course.id,
            "title": course.title,
            "display_title": display_title,
            "slug": course.slug,
            "description": course.description,
            "language_name": language_name,
            "language_flag": language_flag,
            "age_group_name": age_group_name,
            "sessions_count": sessions_count,
            "minutes_per_session": course.minutes_per_session,
        })

        if age_group_name:
            all_age_groups.add(age_group_name)
        if language_name:
            all_languages.add(language_name)

    context = {
        "courses": courses,
        "all_age_groups": sorted(all_age_groups),
        "all_languages": sorted(all_languages),
    }

    return render(request, "website/home.html", context)