from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied

from apps.users.forms.profile import UserAccountForm, ClassParticipationForm
from apps.users.models import ClassParticipation


@login_required
def dashboard_view(request):
    user = request.user

    if request.method == "POST":
        form = UserAccountForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("dashboard")
    else:
        form = UserAccountForm(instance=user)

    participation_history = (
        ClassParticipation.objects.filter(
            Q(volunteers=user) |
            Q(volunteer=user) |
            Q(other_volunteers=user) |
            Q(teacher=user)
        )
        .select_related("teacher", "volunteer")
        .prefetch_related("volunteers", "other_volunteers")
        .distinct()
    )

    for entry in participation_history:
        volunteers = entry.all_volunteers
        entry.display_volunteers = volunteers
        entry.volunteer_count = len(volunteers)

        if entry.teacher_id == user.id:
            entry.user_participation_role = "Teacher"
        elif any(v.id == user.id for v in volunteers):
            entry.user_participation_role = "Volunteer"
        else:
            entry.user_participation_role = "Participant"

    context = {
        "form": form,
        "participation_history": participation_history,
    }
    return render(request, "users/profile.html", context)


@login_required
def create_class_participation_view(request):
    if request.user.role not in ["volunteer", "teacher", "admin"]:
        raise PermissionDenied("You are not allowed to create a class participation.")

    if request.method == "POST":
        form = ClassParticipationForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "The class participation has been created.")
            return redirect("dashboard")
    else:
        form = ClassParticipationForm(user=request.user)

    selected_volunteer_ids = [str(v) for v in (form["volunteers"].value() or [])]

    volunteer_options = (
        form.fields["volunteers"].queryset
        .exclude(id=request.user.id)
        .order_by("username")
    )
    return render(
        request,
        "users/create_class_participation.html",
        {
            "form": form,
            "volunteer_options": volunteer_options,
            "selected_volunteer_ids": selected_volunteer_ids,
        },
    )