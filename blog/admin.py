from django.contrib import admin

from blog.models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Настройка панели администратора для блоговых записей."""

    list_display = ("id", "title", "created_at", "is_published", "views_count")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "content")
