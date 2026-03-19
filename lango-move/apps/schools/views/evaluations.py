from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.schools.forms import ClassTopicEvaluationForm
from apps.schools.models import Classroom, School, ClassTopicEvaluation
from apps.users.models import UserRole


@login_required
def my_schools_and_classes_view(request):
    user = request.user

    teacher_schools = School.objects.none()
    teacher_classrooms = Classroom.objects.none()
    volunteer_schools = School.objects.none()
    volunteer_classrooms = Classroom.objects.none()

    if user.role == UserRole.TEACHER:
        teacher_schools = School.objects.filter(
            teacher_memberships__teacher=user,
            teacher_memberships__is_active=True,
        ).distinct()

        teacher_classrooms = Classroom.objects.filter(
            teacher=user
        ).select_related("school", "age_group", "course")

    elif user.role == UserRole.VOLUNTEER:
        volunteer_classrooms = Classroom.objects.filter(
            volunteer_assignments__volunteer=user,
            volunteer_assignments__is_active=True,
        ).select_related("school", "age_group", "teacher", "course").distinct()

        volunteer_schools = School.objects.filter(
            classrooms__volunteer_assignments__volunteer=user,
            classrooms__volunteer_assignments__is_active=True,
        ).distinct()

    elif user.role == UserRole.ADMIN:
        teacher_schools = School.objects.all()
        teacher_classrooms = Classroom.objects.select_related(
            "school", "age_group", "teacher", "course"
        )
        volunteer_schools = School.objects.all()
        volunteer_classrooms = Classroom.objects.select_related(
            "school", "age_group", "teacher", "course"
        )

    recent_evaluations = ClassTopicEvaluation.objects.filter(
        evaluated_by=user
    ).select_related(
        "classroom",
        "classroom__school",
        "topic",
        "course",
        "course_topic",
    ).order_by("-evaluation_date", "-created_at")[:10]

    return render(
        request,
        "website/my_schools_and_classes.html",
        {
            "teacher_schools": teacher_schools,
            "teacher_classrooms": teacher_classrooms,
            "volunteer_schools": volunteer_schools,
            "volunteer_classrooms": volunteer_classrooms,
            "recent_evaluations": recent_evaluations,
        },
    )


@login_required
def create_class_evaluation_view(request):
    initial = {}

    classroom_id = request.GET.get("classroom")
    if classroom_id:
        initial["classroom"] = classroom_id

    if request.method == "POST":
        form = ClassTopicEvaluationForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Evaluation created successfully.")
            return redirect("dashboard")
    else:
        form = ClassTopicEvaluationForm(
            user=request.user,
            initial=initial,
        )

    return render(
        request,
        "schools/create_class_evaluation.html",
        {
            "form": form,
        },
    )