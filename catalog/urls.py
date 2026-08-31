from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),  # Главная страница (пустой путь)
    path("contacts/", views.contacts_view, name="contacts"),  # Страница контактов
]
