from django.contrib import admin
from django import forms

from apps.schools.models import (
    School,
    Classroom,
    ClassroomVolunteerAssignment,
    TeacherSchoolMembership,
    ClassTopicEvaluation,
)
from apps.users.models import UserRole


class ClassroomVolunteerAssignmentInline(admin.TabularInline):
    model = ClassroomVolunteerAssignment
    extra = 1
    autocomplete_fields = ("volunteer",)


class TeacherSchoolMembershipInline(admin.TabularInline):
    model = TeacherSchoolMembership
    extra = 1
    autocomplete_fields = ("school",)


class ClassroomAdminForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teacher"].queryset = self.fields["teacher"].queryset.filter(role=UserRole.TEACHER)


class ClassroomVolunteerAssignmentAdminForm(forms.ModelForm):
    class Meta:
        model = ClassroomVolunteerAssignment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["volunteer"].queryset = self.fields["volunteer"].queryset.filter(role=UserRole.VOLUNTEER)


class TeacherSchoolMembershipAdminForm(forms.ModelForm):
    class Meta:
        model = TeacherSchoolMembership
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teacher"].queryset = self.fields["teacher"].queryset.filter(role=UserRole.TEACHER)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "contact_email", "is_active", "created_at", "updated_at")
    search_fields = ("name", "city", "contact_email")
    list_filter = ("is_active", "city")
    ordering = ("name",)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    form = ClassroomAdminForm
    list_display = ("name", "school", "teacher", "age_group", "academic_year", "is_active")
    search_fields = ("name", "school__name", "teacher__username", "teacher__email")
    list_filter = ("school", "academic_year", "is_active", "age_group")
    autocomplete_fields = ("school", "teacher", "age_group")
    ordering = ("school__name", "name")
    inlines = [ClassroomVolunteerAssignmentInline]


@admin.register(ClassroomVolunteerAssignment)
class ClassroomVolunteerAssignmentAdmin(admin.ModelAdmin):
    form = ClassroomVolunteerAssignmentAdminForm
    list_display = ("classroom", "volunteer", "is_active", "start_date", "end_date")
    search_fields = ("classroom__name", "classroom__school__name", "volunteer__username", "volunteer__email")
    list_filter = ("is_active", "classroom__school")
    autocomplete_fields = ("classroom", "volunteer")


@admin.register(TeacherSchoolMembership)
class TeacherSchoolMembershipAdmin(admin.ModelAdmin):
    form = TeacherSchoolMembershipAdminForm
    list_display = ("teacher", "school", "is_primary", "is_active", "start_date", "end_date")
    search_fields = ("teacher__username", "teacher__email", "school__name")
    list_filter = ("is_primary", "is_active", "school")
    autocomplete_fields = ("teacher", "school")


@admin.register(ClassTopicEvaluation)
class ClassTopicEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        "classroom",
        "topic",
        "course",
        "course_topic",
        "evaluation_date",
        "evaluated_by",
        "follow_up_needed",
    )
    search_fields = (
        "classroom__name",
        "classroom__school__name",
        "topic__name",
        "course__title",
        "course_topic__title",
        "evaluated_by__username",
    )
    list_filter = ("classroom__school", "topic", "course", "follow_up_needed", "evaluation_date")
    autocomplete_fields = ("classroom", "topic", "course", "course_topic", "evaluated_by")