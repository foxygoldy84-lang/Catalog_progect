from django.contrib import admin

from catalog.models import Category, ContactInfo, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройка панели администратора для категорий."""

    list_display = ("id", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Настройка панели администратора для продуктов."""

    list_display = ("id", "name", "price", "category")
    list_filter = ("category",)
    search_fields = ("name", "description")


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """Настройка панели администратора для контактных данных."""

    list_display = ("id", "phone", "email")
