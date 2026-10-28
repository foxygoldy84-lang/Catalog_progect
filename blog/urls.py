from django.urls import path

from . import views
from .apps import BlogConfig

app_name = BlogConfig.name
urlpatterns = [
    # Список опубликованных статей
    path("", views.BlogPostListView.as_view(), name="blogpost_list"),
    # Создание новой статьи
    path("create/", views.BlogPostCreateView.as_view(), name="blogpost_create"),
    # Просмотр отдельной статьи
    path("<int:pk>/", views.BlogPostDetailView.as_view(), name="blogpost_detail"),
    # Редактирование статьи
    path(
        "<int:pk>/edit/",
        views.BlogPostUpdateView.as_view(),
        name="blogpost_update",
    ),
    # Удаление статьи
    path(
        "<int:pk>/delete/",
        views.BlogPostDeleteView.as_view(),
        name="blogpost_delete",
    ),
]
