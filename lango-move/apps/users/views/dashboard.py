from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.users.forms.profile import UserAccountForm
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

    participation_history = ClassParticipation.objects.filter(
        volunteer=user
    ).select_related("teacher").prefetch_related("other_volunteers")

    context = {
        "form": form,
        "participation_history": participation_history,
    }
    return render(request, "users/profile.html", context)