from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils.formats import localize
from PIL import Image

from catalog.forms import MAX_IMAGE_SIZE, ProductForm
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


def make_image_file(
    name="test.png",
    image_format="PNG",
    content_type="image/png",
    extra_bytes=0,
):
    """Создаёт валидный файл изображения для тестов формы."""
    buffer = BytesIO()
    Image.new("RGB", (10, 10), "white").save(buffer, format=image_format)
    content = buffer.getvalue() + b"\0" * extra_bytes
    return SimpleUploadedFile(name, content, content_type=content_type)


class ProductFormValidationTests(TestCase):
    """Проверки валидации и стилизации формы продукта."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Электроника")

    def get_form_data(self, **overrides):
        data = {
            "name": "Смартфон",
            "description": "Хороший телефон",
            "category": self.category.pk,
            "price": "10000.00",
        }
        data.update(overrides)
        return data

    def test_valid_form_is_accepted(self):
        """Корректные данные проходят валидацию."""
        form = ProductForm(data=self.get_form_data())

        self.assertTrue(form.is_valid(), form.errors)

    def test_forbidden_word_in_name_is_rejected(self):
        """Запрещённое слово в названии блокирует форму."""
        form = ProductForm(data=self.get_form_data(name="Лучшее Казино"))

        self.assertFalse(form.is_valid())
        self.assertIn("названии", form.errors["name"][0])
        self.assertIn("казино", form.errors["name"][0])

    def test_forbidden_word_in_description_is_rejected(self):
        """Запрещённые слова в описании блокируют форму."""
        form = ProductForm(data=self.get_form_data(description="Бесплатно и ДЕШЕВО"))

        self.assertFalse(form.is_valid())
        self.assertIn("описании", form.errors["description"][0])

    def test_forbidden_words_are_checked_case_insensitively(self):
        """Запрещённые слова находятся в любом регистре."""
        form = ProductForm(data=self.get_form_data(name="КРИПТОВАЛЮТА"))

        self.assertFalse(form.is_valid())
        self.assertIn("криптовалюта", form.errors["name"][0])

    def test_negative_price_is_rejected(self):
        """Отрицательная цена не проходит валидацию."""
        form = ProductForm(data=self.get_form_data(price="-1.00"))

        self.assertFalse(form.is_valid())
        self.assertIn("не может быть отрицательной", form.errors["price"][0])

    def test_zero_price_is_accepted(self):
        """Нулевая цена допустима."""
        form = ProductForm(data=self.get_form_data(price="0.00"))

        self.assertTrue(form.is_valid(), form.errors)

    def test_png_and_jpeg_images_are_accepted(self):
        """PNG и JPEG проходят проверку формата."""
        for image_format, content_type, name in (
            ("PNG", "image/png", "test.png"),
            ("JPEG", "image/jpeg", "test.jpg"),
        ):
            with self.subTest(image_format=image_format):
                image = make_image_file(name, image_format, content_type)
                form = ProductForm(data=self.get_form_data(), files={"image": image})

                self.assertTrue(form.is_valid(), form.errors)

    def test_gif_image_is_rejected(self):
        """GIF не проходит проверку формата."""
        image = make_image_file("test.gif", "GIF", "image/gif")
        form = ProductForm(data=self.get_form_data(), files={"image": image})

        self.assertFalse(form.is_valid())
        self.assertIn("JPEG или PNG", form.errors["image"][0])

    def test_image_larger_than_5_mb_is_rejected(self):
        """Изображение больше 5 МБ не проходит валидацию."""
        image = make_image_file(extra_bytes=MAX_IMAGE_SIZE)
        form = ProductForm(data=self.get_form_data(), files={"image": image})

        self.assertFalse(form.is_valid())
        self.assertIn("5 МБ", form.errors["image"][0])

    def test_form_fields_are_styled_in_init(self):
        """Стили полей задаются в методе __init__."""
        form = ProductForm()

        self.assertEqual(form.fields["name"].widget.attrs["class"], "form-control")
        self.assertEqual(
            form.fields["description"].widget.attrs["class"], "form-control"
        )
        self.assertEqual(form.fields["price"].widget.attrs["class"], "form-control")
        self.assertEqual(form.fields["category"].widget.attrs["class"], "form-select")
        self.assertEqual(form.fields["image"].widget.attrs["class"], "form-control")
        self.assertEqual(
            form.fields["image"].widget.attrs["accept"], "image/jpeg,image/png"
        )


class ProductCrudTests(TestCase):
    """Проверки редактирования и удаления продуктов."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Электроника")
        cls.product = Product.objects.create(
            name="Смартфон",
            description="Хороший телефон",
            category=cls.category,
            price=10000,
        )

    def test_update_product(self):
        """Товар можно отредактировать через форму."""
        response = self.client.post(
            reverse("catalog:product_update", args=[self.product.pk]),
            {
                "name": "Обновлённый смартфон",
                "description": "Обновлённое описание",
                "category": self.category.pk,
                "price": "12000.00",
            },
        )

        self.assertRedirects(
            response,
            reverse("catalog:product_detail", args=[self.product.pk]),
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Обновлённый смартфон")
        self.assertEqual(str(self.product.price), "12000.00")

    def test_update_with_forbidden_word_shows_error(self):
        """При запрещённом слове товар не обновляется."""
        response = self.client.post(
            reverse("catalog:product_update", args=[self.product.pk]),
            {
                "name": "Крипта",
                "description": "Описание",
                "category": self.category.pk,
                "price": "12000.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("названии", response.context["form"].errors["name"][0])
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Смартфон")

    def test_delete_product(self):
        """Товар можно удалить."""
        response = self.client.post(
            reverse("catalog:product_delete", args=[self.product.pk])
        )

        self.assertRedirects(response, reverse("catalog:home"))
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_create_with_forbidden_word_shows_error(self):
        """Форма создания показывает ошибку для запрещённого слова."""
        count_before = Product.objects.count()
        response = self.client.post(
            reverse("catalog:create_product"),
            {
                "name": "Казино",
                "description": "Описание",
                "category": self.category.pk,
                "price": "100.00",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("названии", response.context["form"].errors["name"][0])
        self.assertEqual(Product.objects.count(), count_before)
