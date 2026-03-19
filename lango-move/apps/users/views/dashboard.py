from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db.models import Q

from apps.users.forms.profile import UserAccountForm
from apps.users.models import UserRole
from apps.schools.models import ClassTopicEvaluation, Classroom
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.schools.models import Classroom, ClassTopicEvaluation


@login_required
def dashboard_view(request):
    profile = request.user
    edit_mode = request.GET.get("edit") == "1"

    if request.method == "POST":
        form = UserAccountForm(
            request.POST,
            request.FILES,
            instance=profile,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("dashboard")
    else:
        form = UserAccountForm(instance=profile)

    teacher_schools = []
    teacher_classrooms = []
    volunteer_schools = []
    volunteer_classrooms = []
    related_evaluations = ClassTopicEvaluation.objects.none()

    if profile.role == UserRole.TEACHER:
        teacher_classrooms = (
            Classroom.objects.filter(teacher=profile)
            .select_related("school", "age_group", "course")
            .order_by("school__name", "name")
        )
        teacher_schools = list({c.school for c in teacher_classrooms})

        related_evaluations = (
            ClassTopicEvaluation.objects
            .filter(classroom__teacher=profile)
            .select_related(
                "classroom",
                "classroom__school",
                "classroom__teacher",
                "topic",
                "course",
                "course_topic",
                "evaluated_by",
            )
            .prefetch_related("classroom__volunteer_assignments__volunteer")
            .order_by("-evaluation_date", "-created_at")
        )

    elif profile.role == UserRole.VOLUNTEER:
        volunteer_classrooms = (
            Classroom.objects.filter(
                volunteer_assignments__volunteer=profile,
                volunteer_assignments__is_active=True,
            )
            .select_related("school", "age_group", "teacher", "course")
            .distinct()
            .order_by("school__name", "name")
        )
        volunteer_schools = list({c.school for c in volunteer_classrooms})

        related_evaluations = (
            ClassTopicEvaluation.objects
            .filter(
                classroom__volunteer_assignments__volunteer=profile,
                classroom__volunteer_assignments__is_active=True,
            )
            .select_related(
                "classroom",
                "classroom__school",
                "classroom__teacher",
                "topic",
                "course",
                "course_topic",
                "evaluated_by",
            )
            .prefetch_related("classroom__volunteer_assignments__volunteer")
            .distinct()
            .order_by("-evaluation_date", "-created_at")
        )

    elif profile.role == UserRole.ADMIN:
        teacher_classrooms = Classroom.objects.select_related("school", "age_group", "teacher", "course")
        volunteer_classrooms = teacher_classrooms
        teacher_schools = list({c.school for c in teacher_classrooms})
        volunteer_schools = teacher_schools

        related_evaluations = (
            ClassTopicEvaluation.objects
            .select_related(
                "classroom",
                "classroom__school",
                "classroom__teacher",
                "topic",
                "course",
                "course_topic",
                "evaluated_by",
            )
            .prefetch_related("classroom__volunteer_assignments__volunteer")
            .order_by("-evaluation_date", "-created_at")
        )

    recent_evaluations = related_evaluations[:10]

    return render(
        request,
        "users/profile.html",
        {
            "profile_user": profile,
            "form": form,
            "edit_mode": edit_mode,
            "teacher_schools": teacher_schools,
            "teacher_classrooms": teacher_classrooms,
            "volunteer_schools": volunteer_schools,
            "volunteer_classrooms": volunteer_classrooms,
            "recent_evaluations": recent_evaluations,
        },
    )


@login_required
def volunteer_dashboard_view(request):
    user = request.user

    classrooms = (
        Classroom.objects.filter(
            volunteer_assignments__volunteer=user,
            volunteer_assignments__is_active=True,
        )
        .select_related("school", "teacher", "age_group", "course")
        .distinct()
        .order_by("school__name", "name")
    )

    recent_evaluations = (
        ClassTopicEvaluation.objects
        .filter(classroom__in=classrooms)
        .select_related(
            "classroom",
            "classroom__school",
            "classroom__teacher",
            "topic",
            "course",
            "course_topic",
            "evaluated_by",
        )
        .prefetch_related("classroom__volunteer_assignments__volunteer")
        .order_by("-evaluation_date", "-created_at")[:20]
    )

    school_map = {}
    for classroom in classrooms:
        school = classroom.school
        if school.id not in school_map:
            school_map[school.id] = {
                "school": school,
                "classrooms": [],
            }
        school_map[school.id]["classrooms"].append(classroom)

    context = {
        "school_groups": list(school_map.values()),
        "recent_evaluations": recent_evaluations,
    }

    return render(request, "users/volunteer_dashboard.html", context)