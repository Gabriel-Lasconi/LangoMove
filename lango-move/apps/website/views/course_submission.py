from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from apps.curriculum.forms import (
    CourseModerationForm,
    CourseSubmissionForm,
    CourseTopicBuilderFormSet,
)
from apps.curriculum.models import Course, CourseStatus, CourseTopic, CourseTopicGame
from apps.users.models import UserRole


def _can_submit_course(user):
    return user.is_authenticated and user.role in [
        UserRole.ADMIN,
        UserRole.TEACHER,
        UserRole.VOLUNTEER,
    ]


def _is_admin(user):
    return user.is_authenticated and user.role == UserRole.ADMIN


def _generate_unique_course_topic_slug(course, title, sequence_number, instance_pk=None):
    base = slugify(f"{course.slug}-session-{sequence_number}-{title or 'topic'}") or f"{course.slug}-session-{sequence_number}"
    slug = base
    counter = 2

    queryset = CourseTopic.objects.all()
    if instance_pk:
        queryset = queryset.exclude(pk=instance_pk)

    while queryset.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1

    return slug


@login_required
def course_submission_list_view(request):
    if not _can_submit_course(request.user):
        messages.error(request, "You do not have permission to access this page.")
        return redirect("home")

    if _is_admin(request.user):
        courses = Course.objects.select_related("language", "age_group", "created_by").order_by("-created_at")
    else:
        courses = (
            Course.objects
            .select_related("language", "age_group", "created_by")
            .filter(created_by=request.user)
            .order_by("-created_at")
        )

    return render(
        request,
        "website/course_submission_list.html",
        {"courses": courses},
    )


@login_required
def course_create_view(request):
    if not _can_submit_course(request.user):
        messages.error(request, "You do not have permission to create a course.")
        return redirect("home")

    if request.method == "POST":
        form = CourseSubmissionForm(request.POST)
        if form.is_valid():
            course = form.save(created_by=request.user)
            messages.success(request, "Course basics saved. Now configure the sessions.")
            return redirect("course-build-sessions", pk=course.pk)
    else:
        form = CourseSubmissionForm()

    return render(
        request,
        "website/course_create.html",
        {"form": form},
    )


@login_required
def course_build_sessions_view(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if not (_is_admin(request.user) or course.created_by == request.user):
        messages.error(request, "You do not have permission to configure this course.")
        return redirect("home")

    existing_topics = list(
        course.course_topics.prefetch_related("course_topic_games__game").order_by("sequence_number")
    )

    initial_data = []
    if existing_topics:
        for topic in existing_topics:
            existing_games = [link.game for link in topic.course_topic_games.all().order_by("order_in_topic")]
            initial_data.append({
                "topic": topic.topic,
                "title": topic.title,
                "grammar_objectives": topic.grammar_objectives,
                "lexical_objectives": topic.lexical_objectives,
                "action_objectives": topic.action_objectives,
                "game_1": existing_games[0].pk if len(existing_games) > 0 else None,
                "game_2": existing_games[1].pk if len(existing_games) > 1 else None,
                "game_3": existing_games[2].pk if len(existing_games) > 2 else None,
                "game_4": existing_games[3].pk if len(existing_games) > 3 else None,
                "game_5": existing_games[4].pk if len(existing_games) > 4 else None,
            })
    else:
        for i in range(course.sessions_count):
            initial_data.append({"title": f"Session {i + 1}"})

    if request.method == "POST":
        formset = CourseTopicBuilderFormSet(request.POST, initial=initial_data)

        for index, form in enumerate(formset.forms, start=1):
            form.session_number = index

        if formset.is_valid():
            course.course_topics.all().delete()

            for index, form in enumerate(formset.forms, start=1):
                data = form.cleaned_data
                topic = data.get("topic")
                title = data.get("title") or (topic.name if topic else f"Session {index}")

                course_topic = CourseTopic.objects.create(
                    course=course,
                    topic=topic,
                    title=title,
                    sequence_number=index,
                    slug=_generate_unique_course_topic_slug(course, title, index),
                    grammar_objectives=data.get("grammar_objectives") or "",
                    lexical_objectives=data.get("lexical_objectives") or "",
                    action_objectives=data.get("action_objectives") or "",
                    status="published",
                )

                selected_games = form.get_selected_games()
                for game_index, game in enumerate(selected_games, start=1):
                    CourseTopicGame.objects.create(
                        course_topic=course_topic,
                        game=game,
                        order_in_topic=game_index,
                    )

            messages.success(request, "Course sessions saved successfully.")
            return redirect("course-submission-list")
    else:
        formset = CourseTopicBuilderFormSet(initial=initial_data)
        for index, form in enumerate(formset.forms, start=1):
            form.session_number = index

    session_forms = list(enumerate(formset.forms, start=1))

    return render(
        request,
        "website/course_build_sessions.html",
        {
            "course": course,
            "formset": formset,
            "session_forms": session_forms,
        },
    )


@login_required
def course_edit_view(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if not (_is_admin(request.user) or course.created_by == request.user):
        messages.error(request, "You do not have permission to edit this course.")
        return redirect("home")

    if request.method == "POST":
        form = CourseSubmissionForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save(created_by=course.created_by or request.user)
            course.status = CourseStatus.DRAFT
            course.approved_by = None
            course.approved_at = None
            course.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
            messages.success(request, "Course updated. You can now review the sessions again.")
            return redirect("course-build-sessions", pk=course.pk)
    else:
        form = CourseSubmissionForm(instance=course)

    return render(
        request,
        "website/course_create.html",
        {
            "form": form,
            "course": course,
            "edit_mode": True,
        },
    )


@login_required
def course_moderation_list_view(request):
    if not _is_admin(request.user):
        messages.error(request, "Admin access required.")
        return redirect("home")

    courses = (
        Course.objects
        .select_related("language", "age_group", "created_by", "approved_by")
        .order_by("status", "-created_at")
    )

    return render(
        request,
        "website/course_moderation_list.html",
        {"courses": courses},
    )


@login_required
def course_moderation_detail_view(request, pk):
    if not _is_admin(request.user):
        messages.error(request, "Admin access required.")
        return redirect("home")

    course = get_object_or_404(
        Course.objects.select_related("language", "age_group", "created_by", "approved_by"),
        pk=pk,
    )

    if request.method == "POST":
        form = CourseModerationForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save(commit=False)

            if course.status == CourseStatus.PUBLISHED:
                course.approved_by = request.user
                course.approved_at = timezone.now()
            elif course.status != CourseStatus.PUBLISHED:
                course.approved_by = None
                course.approved_at = None

            course.save()
            messages.success(request, "Course moderation updated.")
            return redirect("course-moderation-list")
    else:
        form = CourseModerationForm(instance=course)

    return render(
        request,
        "website/course_moderation_detail.html",
        {
            "course": course,
            "form": form,
        },
    )