from django.urls import path

from . import views
from .apps import CatalogConfig

app_name = CatalogConfig.name
urlpatterns = [
    path("", views.home_view, name="home"),  # Главная страница (пустой путь)
    path("contacts/", views.contacts_view, name="contacts"),  # Страница контактов
    path("create/", views.create_product_view, name="create_product"),
    # Подробная информация о конкретном товаре
    path("products/<int:pk>/", views.product_detail_view, name="product_detail"),
]
