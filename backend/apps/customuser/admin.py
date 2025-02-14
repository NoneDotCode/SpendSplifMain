from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from backend.apps.customuser.models import CustomUser
from django import forms


class CustomUserAdminForm(forms.ModelForm):
    roles = forms.ChoiceField(
        choices=[
            ("free", "Free"),
            ("business_plan", "Business plan"),
            ("business_member_lic", "Business member license"),
            ("business_member_plan", "Business member plan"),
            ("business_lic", "Business license"),
            ("sponsor", "Sponsor"),
            ("employee", "Employee"),
        ],
        widget=forms.Select,  # Один вибір
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ["roles"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.roles:
            self.fields["roles"].initial = self.instance.roles  # Тепер одне значення, а не список

    def clean_roles(self):
        return self.cleaned_data["roles"]


class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm
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
        "roles",
    )
    search_fields = ("email",)
    list_filter = ("roles",)

    def get_roles(self, obj):
        return obj.roles if obj.roles else "No role"

    get_roles.short_description = "Role"

    list_editable = ("roles",)


admin.site.register(CustomUser, CustomUserAdmin)

