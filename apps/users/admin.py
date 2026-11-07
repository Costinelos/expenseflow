from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "role", "approval_limit", "is_staff", "is_active"]
    list_filter = ["role", "is_staff", "is_active"]
    search_fields = ["email"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "ExpenseFlow Info",
            {"fields": ("role", "approval_limit")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "approval_limit"),
            },
        ),
    )