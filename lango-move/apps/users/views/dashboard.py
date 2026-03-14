from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db.models import Q
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
    if profile.role in [UserRole.VOLUNTEER, UserRole.TEACHER, UserRole.ADMIN]:
        participations = ClassParticipation.objects.none()

        if profile.role in [UserRole.VOLUNTEER, UserRole.TEACHER, UserRole.ADMIN]:
            participations = (
                ClassParticipation.objects.filter(
                    Q(volunteers=profile) | Q(teacher=profile)
                )
                .select_related("teacher")
                .prefetch_related("volunteers")
                .distinct()
                .order_by("-date", "-id")
            )

        for participation in participations:
            volunteers = list(participation.volunteers.all())

            class_history.append({
                "id": participation.id,
                "school_name": participation.school_name,
                "date": participation.date,
                "children_group": participation.children_group,
                "language": participation.language,
                "session_title": participation.session_title,
                "teacher": participation.teacher,
                "volunteers": volunteers,
                "notes": participation.notes,
            })

    return render(
        request,
        "users/profile.html",
        {
            "profile_user": profile,
            "form": form,
            "edit_mode": edit_mode,
            "class_history": class_history,
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