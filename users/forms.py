from django import forms
from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm

from users.models import User


class RegistrationForm(BaseUserCreationForm):
    """Форма регистрации пользователя по электронной почте и паролю."""

    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ("email", "avatar", "phone", "country")
        field_classes = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Единый стиль полей формы, как в остальных формах проекта
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            else:
                widget.attrs["class"] = "form-control"

        self.fields["avatar"].widget.attrs["accept"] = "image/*"

        for name, placeholder in (
            ("email", "you@example.com"),
            ("phone", "+7 999 123-45-67"),
            ("country", "Россия"),
        ):
            self.fields[name].widget.attrs.setdefault("placeholder", placeholder)

    def clean_email(self):
        """Приводит электронную почту к нижнему регистру."""
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Пользователь с такой электронной почтой уже зарегистрирован."
            )
        return email


class EmailAuthenticationForm(AuthenticationForm):
    """Форма входа, в которой вместо имени пользователя вводится email."""

    username = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autofocus": True,
                "autocomplete": "email",
                "placeholder": "you@example.com",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "current-password",
            }
        ),
    )
