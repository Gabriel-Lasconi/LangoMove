from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.users.models import User, ClassParticipation


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "username", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")
    ordering = ("email",)
    search_fields = ("email", "username", "city", "country")

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Profile information",
            {
                "fields": (
                    "role",
                    "photo",
                    "date_of_birth",
                    "phone",
                    "city",
                    "country",
                    "bio",
                )
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Additional information",
            {
                "fields": (
                    "email",
                    "role",
                    "photo",
                    "date_of_birth",
                    "phone",
                    "city",
                    "country",
                    "bio",
                )
            },
        ),
    )


@admin.register(ClassParticipation)
class ClassParticipationAdmin(admin.ModelAdmin):
    list_display = ("date", "school_name", "language", "teacher", "display_volunteers")
    list_filter = ("language", "date")
    search_fields = (
        "school_name",
        "children_group",
        "session_title",
        "teacher__username",
        "teacher__email",
        "volunteers__username",
        "volunteers__email",
    )
    filter_horizontal = ("volunteers",)
    fields = (
        "date",
        "school_name",
        "children_group",
        "language",
        "session_title",
        "teacher",
        "volunteers",
        "notes",
    )

    def display_volunteers(self, obj):
        volunteers = obj.all_volunteers
        if not volunteers:
            return "-"
        return ", ".join(user.username for user in volunteers)

    display_volunteers.short_description = "Volunteers"