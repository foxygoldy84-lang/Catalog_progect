from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

from users.models import User


class CustomUserChangeForm(UserChangeForm):
    """Форма изменения пользователя в административной панели."""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


class CustomUserCreationForm(AdminUserCreationForm):
    """Форма создания пользователя в административной панели."""

    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {}


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Настройки отображения пользователей в административной панели."""

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = User

    list_display = ("email", "first_name", "last_name", "phone", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "country")
    search_fields = ("email", "first_name", "last_name", "phone")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Личная информация"),
            {"fields": ("first_name", "last_name", "avatar", "phone", "country")},
        ),
        (
            _("Права доступа"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Важные даты"),
            {"fields": ("last_login", "date_joined")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "usable_password", "password1", "password2"),
            },
        ),
    )
