from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.customuser.models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Add any additional fields you want to display in the user list view
    list_display = (
        "id",
        "username",
        "email",
        "language",
        "tag",
        "password",
        "is_staff",
        "is_active",
        "date_joined",
    )


# Register your custom admin
admin.site.register(CustomUser, CustomUserAdmin)
