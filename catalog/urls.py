from django.urls import path

from . import views
from .apps import CatalogConfig

app_name = CatalogConfig.name
urlpatterns = [
    # Главная страница (пустой путь)
    path("", views.HomeView.as_view(), name="home"),
    # Страница контактов
    path("contacts/", views.ContactsView.as_view(), name="contacts"),
    # Добавление нового товара
    path("create/", views.ProductCreateView.as_view(), name="create_product"),
    # Подробная информация о конкретном товаре
    path(
        "products/<int:pk>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
]
