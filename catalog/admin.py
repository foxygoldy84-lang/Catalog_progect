from django.contrib import admin
from catalog.models import Category, Product, ContactInfo


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройка панели администратора для категорий."""
    # Выводим id и name в списке категорий
    list_display = ("id", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Настройка панели администратора для продуктов."""
    # Выводим id, name, price и category в списке продуктов
    list_display = ("id", "name", "price", "category")

    # Настраиваем фильтрацию продуктов по категории
    list_filter = ("category",)

    # Настраиваем поиск по полям name и description
    search_fields = ("name", "description")


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """Настройка панели администратора для контактных данных."""
    # Выводим телефон и почту компании
    list_display = ("id", "phone", "email")
