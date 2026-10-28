from django.urls import path

from . import views
from .apps import UsersConfig

app_name = UsersConfig.name
urlpatterns = [
    # Регистрация нового пользователя
    path("register/", views.RegisterView.as_view(), name="register"),
    # Вход по электронной почте и паролю
    path("login/", views.UserLoginView.as_view(), name="login"),
    # Выход из аккаунта
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
]
