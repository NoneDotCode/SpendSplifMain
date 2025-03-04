from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from backend.apps.customuser.models import CustomUser


class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = "__all__"

    roles = forms.MultipleChoiceField(
        choices=CustomUser.roles_choices,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["roles"].initial = self.instance.roles

        # Убедимся, что обязательные поля заполняются
        self.fields["email"].required = True
        self.fields["username"].required = True
        self.fields["password"].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.roles = self.cleaned_data["roles"]

        # Проверяем, изменился ли пароль
        if "password" in self.changed_data and self.cleaned_data["password"]:
            instance.set_password(self.cleaned_data["password"])

        if commit:
            instance.save()
        return instance


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    filter_horizontal = ("groups", "user_permissions")
    form = CustomUserAdminForm
    list_display = (
        "id",
        "username",
        "email",
        "language",
        "tag",
        "is_staff",
        "is_active",
        "date_joined",
    )

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal Info", {"fields": ("language", "tag")}),
        ("Roles", {"fields": ("roles",)}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )

    ordering = ("id",)
    search_fields = ("email", "username")
    actions = ["make_employee"]

    @admin.action(description="Назначить роль Employee")
    def make_employee(self, request, queryset):
        updated_count = 0
        for user in queryset:
            if "employee" not in user.roles:
                user.roles.append("employee")
                user.save()
                updated_count += 1
        self.message_user(request, _(f"Роль Employee выдана {updated_count} пользователям."), messages.SUCCESS)