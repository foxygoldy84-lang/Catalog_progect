from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import EmailAuthenticationForm, RegistrationForm


class RegisterView(CreateView):
    """Регистрация пользователя с отправкой приветственного письма."""

    form_class = RegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.send_welcome_email(self.object)
        messages.success(
            self.request,
            "Регистрация прошла успешно. Теперь можно войти в аккаунт.",
        )
        return response

    @staticmethod
    def send_welcome_email(user):
        """Отправляет приветственное письмо новому пользователю."""
        send_mail(
            subject="Добро пожаловать в Каталог товаров!",
            message=(
                f"Здравствуйте, {user.email}!\n\n"
                "Спасибо за регистрацию в нашем каталоге.\n"
                "Теперь вам доступны создание, редактирование и удаление товаров.\n\n"
                "Желаем приятной работы!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )


class UserLoginView(LoginView):
    """Вход на сайт по электронной почте и паролю."""

    template_name = "users/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    """Выход из аккаунта."""

    next_page = reverse_lazy("catalog:home")
