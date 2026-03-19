from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.shortcuts import redirect, render

from apps.schools.models import Classroom, ClassTopicEvaluation, School
from apps.users.forms.profile import UserAccountForm, ClassParticipationForm
from apps.users.models import ClassParticipation, UserRole


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

    class_history = []
    recent_evaluations = ClassTopicEvaluation.objects.none()

    if profile.role in [UserRole.VOLUNTEER, UserRole.TEACHER, UserRole.ADMIN]:
        participations = (
            ClassParticipation.objects.filter(
                Q(volunteers=profile) | Q(teacher=profile)
            )
            .select_related("teacher", "school", "classroom", "classroom__school", "classroom__age_group")
            .prefetch_related("volunteers")
            .distinct()
            .order_by("-date", "-id")
        )

        for participation in participations:
            volunteers = list(participation.volunteers.all())

            class_history.append({
                "id": participation.id,
                "school_name": participation.resolved_school_name,
                "date": participation.date,
                "children_group": participation.resolved_children_group,
                "language": participation.language,
                "session_title": participation.session_title,
                "teacher": participation.teacher,
                "volunteers": volunteers,
                "notes": participation.notes,
                "school": participation.school,
                "classroom": participation.classroom,
            })

        recent_evaluations = ClassTopicEvaluation.objects.filter(
            evaluated_by=profile
        ).select_related(
            "classroom",
            "classroom__school",
            "topic",
            "course",
            "course_topic",
        ).order_by("-evaluation_date", "-created_at")[:5]

    return render(
        request,
        "users/profile.html",
        {
            "profile_user": profile,
            "form": form,
            "edit_mode": edit_mode,
            "class_history": class_history,
            "recent_evaluations": recent_evaluations,
        },
    )


@login_required
def volunteer_dashboard_view(request):
    profile = request.user

    if profile.role not in [UserRole.VOLUNTEER, UserRole.ADMIN]:
        messages.error(request, "This page is only available for volunteers.")
        return redirect("dashboard")

    classroom_queryset = (
        Classroom.objects.filter(
            volunteer_assignments__volunteer=profile,
            volunteer_assignments__is_active=True,
            is_active=True,
        )
        .select_related("school", "age_group", "teacher")
        .distinct()
        .order_by("school__name", "name")
    )

    schools_map = OrderedDict()

    for classroom in classroom_queryset:
        school = classroom.school
        if school.id not in schools_map:
            schools_map[school.id] = {
                "school": school,
                "classrooms": [],
            }
        schools_map[school.id]["classrooms"].append(classroom)

    recent_evaluations = ClassTopicEvaluation.objects.filter(
        evaluated_by=profile
    ).select_related(
        "classroom",
        "classroom__school",
        "topic",
    ).order_by("-evaluation_date", "-created_at")[:8]

    return render(
        request,
        "users/volunteer_dashboard.html",
        {
            "profile_user": profile,
            "school_groups": list(schools_map.values()),
            "recent_evaluations": recent_evaluations,
        },
    )


@login_required
def create_class_participation_view(request):
    if request.method == "POST":
        form = ClassParticipationForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Class participation created successfully.")
            return redirect("dashboard")
    else:
        form = ClassParticipationForm(user=request.user)

    selected_volunteer_ids = [str(v) for v in (form["volunteers"].value() or [])]
    selected_teacher_id = str(form["teacher"].value() or "")

    volunteer_options = (
        form.fields["volunteers"].queryset
        .exclude(id=request.user.id)
        .order_by("username")
    )
    teacher_options = form.fields["teacher"].queryset.order_by("username")

    return render(
        request,
        "users/create_class_participation.html",
        {
            "form": form,
            "volunteer_options": volunteer_options,
            "teacher_options": teacher_options,
            "selected_volunteer_ids": selected_volunteer_ids,
            "selected_teacher_id": selected_teacher_id,
        },
    )