from django.test import TestCase
from django.urls import reverse
from django.utils.formats import localize

from catalog.models import Category, Product


class CatalogViewTests(TestCase):
    """Проверки контроллеров и шаблонов каталога."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Электроника",
            description="Бытовая техника и гаджеты",
        )
        # Описание заведомо длиннее 100 символов, чтобы проверить обрезку
        cls.product = Product.objects.create(
            name="Смартфон",
            description="Подробное описание товара. " * 20,
            category=cls.category,
            price=29999.99,
        )

    def test_home_view_shows_product_list(self):
        """Главная страница выводит карточки товаров."""
        response = self.client.get(reverse("catalog:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, "Подробнее")

    def test_home_view_truncates_description(self):
        """Описание в карточке обрезается до первых 100 символов."""
        response = self.client.get(reverse("catalog:home"))

        self.assertContains(response, self.product.description[:99] + "…")
        self.assertNotContains(response, self.product.description)

    def test_product_detail_view_shows_all_product_info(self):
        """Страница товара содержит всю информацию о товаре."""
        url = reverse("catalog:product_detail", args=[self.product.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)
        self.assertContains(response, self.category.name)
        self.assertContains(response, localize(self.product.price))
        self.assertContains(response, self.product.created_at.strftime("%d.%m.%Y"))

    def test_product_detail_view_returns_404_for_missing_product(self):
        """Несуществующий товар возвращает страницу 404."""
        url = reverse("catalog:product_detail", args=[99999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class PaginationTests(TestCase):
    """Проверки постраничного вывода списка товаров."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Одежда")
        for number in range(7):
            Product.objects.create(
                name=f"Товар {number}",
                description="Описание товара",
                category=cls.category,
                price=100 + number,
            )

    def test_first_page_contains_first_part_of_products(self):
        """На первой странице выводится только первая часть товаров."""
        response = self.client.get(reverse("catalog:home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 6)
        self.assertTrue(response.context["page_obj"].has_next())
        self.assertEqual(response.context["page_obj"].paginator.num_pages, 2)

    def test_second_page_contains_remaining_products(self):
        """На второй странице выводится оставшаяся часть товаров."""
        response = self.client.get(reverse("catalog:home"), {"page": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.assertFalse(response.context["page_obj"].has_next())
        self.assertContains(response, "Товар 0")
        self.assertNotContains(response, "Товар 6")

    def test_invalid_page_number_falls_back_to_first_page(self):
        """Некорректный номер страницы показывает первую страницу."""
        response = self.client.get(reverse("catalog:home"), {"page": "abc"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 1)

    def test_pagination_links_are_rendered(self):
        """На странице выводятся ссылки для перехода между страницами."""
        response = self.client.get(reverse("catalog:home"))

        self.assertContains(response, "?page=2")
        self.assertContains(response, "Вперёд")


class CreateProductTests(TestCase):
    """Проверки страницы добавления нового товара."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Электроника")

    def test_create_page_is_rendered(self):
        """Страница добавления отображает форму."""
        response = self.client.get(reverse("catalog:create_product"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Добавить новый товар")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_warning_is_shown_when_there_are_no_categories(self):
        """Если категорий нет, пользователь получает подсказку."""
        Category.objects.all().delete()

        response = self.client.get(reverse("catalog:create_product"))

        self.assertContains(response, "ни одной категории")

    def test_valid_form_saves_product_to_database(self):
        """Отправка корректных данных сохраняет товар в базе."""
        response = self.client.post(
            reverse("catalog:create_product"),
            {
                "name": "Планшет",
                "description": "Новый планшет",
                "category": self.category.pk,
                "price": "12500.00",
            },
        )

        self.assertRedirects(response, reverse("catalog:home"))
        self.assertTrue(Product.objects.filter(name="Планшет").exists())

        product = Product.objects.get(name="Планшет")
        self.assertEqual(product.category, self.category)
        self.assertEqual(str(product.price), "12500.00")

    def test_invalid_form_shows_errors_and_saves_nothing(self):
        """Ошибочные данные показываются пользователю и не сохраняются."""
        response = self.client.post(
            reverse("catalog:create_product"),
            {"name": "", "description": "Описание", "price": "100"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(Product.objects.count(), 0)

    def test_success_message_is_shown_on_home_page(self):
        """После добавления товара показывается сообщение об успехе."""
        self.client.post(
            reverse("catalog:create_product"),
            {
                "name": "Наушники",
                "description": "Беспроводные наушники",
                "category": self.category.pk,
                "price": "4990.00",
            },
        )

        response = self.client.get(reverse("catalog:home"))

        self.assertContains(response, "успешно добавлен в каталог")
