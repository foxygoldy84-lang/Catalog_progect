import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from catalog.models import Category, Product


class Command(BaseCommand):
    """Кастомная команда для очистки БД и заполнения данными из фикстур с поддержкой UTF-8."""
    help = "Очищает базу данных и загружает новые тестовые данные из фикстур JSON"

    def handle(self, *args, **options):
        # 1. Очищаем старые данные
        self.stdout.write(self.style.WARNING("Очистка базы данных..."))
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("База данных успешно очищена."))

        # Путь к папке с фикстурами
        fixtures_dir = os.path.join(settings.BASE_DIR, 'catalog', 'fixtures')

        # 2. Загружаем категории
        category_file = os.path.join(fixtures_dir, 'category_data.json')
        self.stdout.write("Загрузка категорий товаров...")

        try:
            with open(category_file, 'r', encoding='utf-8') as f:
                categories_data = json.load(f)

            for item in categories_data:
                Category.objects.create(
                    id=item['pk'],
                    name=item['fields']['name'],
                    description=item['fields']['description']
                )
            self.stdout.write(self.style.SUCCESS("Категории успешно загружены."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка загрузки категорий: {e}"))
            return

        # 3. Загружаем продукты
        product_file = os.path.join(fixtures_dir, 'product_data.json')
        self.stdout.write("Загрузка продуктов...")

        try:
            with open(product_file, 'r', encoding='utf-8') as f:
                products_data = json.load(f)

            for item in products_data:
                category_id = item['fields']['category']
                category_instance = Category.objects.get(id=category_id)

                Product.objects.create(
                    id=item['pk'],
                    name=item['fields']['name'],
                    description=item['fields']['description'],
                    image=item['fields'].get('image'),
                    price=item['fields']['price'],
                    category=category_instance
                )
            self.stdout.write(self.style.SUCCESS("Все тестовые данные успешно загружены в PostgreSQL!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка загрузки продуктов: {e}"))
