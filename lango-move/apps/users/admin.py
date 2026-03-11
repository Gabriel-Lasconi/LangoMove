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
    list_display = ("date", "volunteer", "school_name", "language", "teacher")
    list_filter = ("language", "date")
    search_fields = ("school_name", "children_group", "session_title", "volunteer__username", "teacher__username")
    filter_horizontal = ("other_volunteers",)