from urllib.parse import unquote

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import FieldDoesNotExist
from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product

User = get_user_model()


class UserModelTests(TestCase):
    """Проверки кастомной модели пользователя."""

    def test_user_is_created_with_email(self):
        """Пользователь создаётся по email, пароль сохраняется в виде хеша."""
        user = User.objects.create_user(
            email="User@Example.com",
            password="Strong-password-123",
        )

        self.assertEqual(user.email, "User@example.com")
        self.assertTrue(user.check_password("Strong-password-123"))
        self.assertNotEqual(user.password, "Strong-password-123")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_email_is_username_field(self):
        """Полем авторизации является email, а username не используется."""
        self.assertEqual(User.USERNAME_FIELD, "email")
        self.assertEqual(User.REQUIRED_FIELDS, [])

        with self.assertRaises(FieldDoesNotExist):
            User._meta.get_field("username")

    def test_superuser_is_created_with_flags(self):
        """create_superuser выдаёт права администратора."""
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="Admin-password-123",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_extra_fields_are_saved(self):
        """Аватар, телефон и страна сохраняются в модели."""
        user = User.objects.create_user(
            email="profile@example.com",
            password="Strong-password-123",
            phone="+7 999 123-45-67",
            country="Россия",
        )

        self.assertEqual(user.phone, "+7 999 123-45-67")
        self.assertEqual(user.country, "Россия")
        self.assertFalse(user.avatar)


class RegistrationTests(TestCase):
    """Проверки регистрации и приветственного письма."""

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("users:register")

    def test_registration_page_is_rendered(self):
        """Страница регистрации содержит форму с email и паролями."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Регистрация")
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

    def test_successful_registration_creates_user_and_sends_email(self):
        """После регистрации создаётся пользователь и уходит письмо."""
        response = self.client.post(
            self.url,
            {
                "email": "newuser@example.com",
                "password1": "Strong-password-123",
                "password2": "Strong-password-123",
                "phone": "+7 900 000-00-00",
                "country": "Россия",
            },
        )

        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

        user = User.objects.get(email="newuser@example.com")
        self.assertEqual(user.phone, "+7 900 000-00-00")
        self.assertEqual(user.country, "Россия")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["newuser@example.com"])
        self.assertIn("Добро пожаловать", mail.outbox[0].subject)

    def test_registration_with_existing_email_is_rejected(self):
        """Нельзя зарегистрировать два аккаунта на один email."""
        User.objects.create_user(
            email="existing@example.com",
            password="Strong-password-123",
        )

        response = self.client.post(
            self.url,
            {
                "email": "Existing@Example.com",
                "password1": "Strong-password-123",
                "password2": "Strong-password-123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_passwords_must_match(self):
        """Форма не принимает разные пароли."""
        response = self.client.post(
            self.url,
            {
                "email": "newuser@example.com",
                "password1": "Strong-password-123",
                "password2": "Another-password-456",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("password2", response.context["form"].errors)
        self.assertFalse(User.objects.filter(email="newuser@example.com").exists())

    def test_email_is_saved_in_lowercase(self):
        """Email приводится к нижнему регистру при регистрации."""
        self.client.post(
            self.url,
            {
                "email": "MixedCase@Example.com",
                "password1": "Strong-password-123",
                "password2": "Strong-password-123",
            },
        )

        self.assertTrue(User.objects.filter(email="mixedcase@example.com").exists())


class AuthenticationTests(TestCase):
    """Проверки входа по email и выхода из аккаунта."""

    @classmethod
    def setUpTestData(cls):
        cls.password = "Strong-password-123"
        cls.user = User.objects.create_user(
            email="login@example.com",
            password=cls.password,
        )

    def test_login_page_is_rendered(self):
        """Страница входа содержит поле email и пароль."""
        response = self.client.get(reverse("users:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Электронная почта")
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_login_by_email_and_password(self):
        """Пользователь входит по электронной почте и паролю."""
        response = self.client.post(
            reverse("users:login"),
            {
                "username": "login@example.com",
                "password": self.password,
            },
        )

        self.assertRedirects(response, reverse("catalog:home"))
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk,
        )

    def test_login_with_wrong_password_fails(self):
        """Неверный пароль не авторизует пользователя."""
        response = self.client.post(
            reverse("users:login"),
            {
                "username": "login@example.com",
                "password": "wrong-password",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_ends_session(self):
        """Выход завершает сессию и возвращает на главную."""
        self.client.force_login(self.user)

        response = self.client.post(reverse("users:logout"))

        self.assertRedirects(response, reverse("catalog:home"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ProductAccessTests(TestCase):
    """Проверки ограничения доступа к управлению продуктами."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Электроника")
        cls.product = Product.objects.create(
            name="Смартфон",
            description="Хороший телефон",
            category=cls.category,
            price=10000,
        )
        cls.user = User.objects.create_user(
            email="manager@example.com",
            password="Strong-password-123",
        )

    def get_protected_urls(self):
        """URL-адреса страниц, доступных только авторизованным пользователям."""
        return [
            reverse("catalog:product_detail", args=[self.product.pk]),
            reverse("catalog:create_product"),
            reverse("catalog:product_update", args=[self.product.pk]),
            reverse("catalog:product_delete", args=[self.product.pk]),
        ]

    def test_home_page_is_public(self):
        """Список товаров доступен без авторизации."""
        response = self.client.get(reverse("catalog:home"))

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_is_redirected_to_login(self):
        """Анонимный пользователь перенаправляется на страницу входа."""
        for url in self.get_protected_urls():
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("users:login"), response.url)
                self.assertIn(url, unquote(response.url))

    def test_anonymous_user_cannot_delete_product(self):
        """Анонимный пользователь не может удалить товар."""
        response = self.client.post(
            reverse("catalog:product_delete", args=[self.product.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_authenticated_user_can_open_protected_pages(self):
        """Авторизованный пользователь видит все страницы управления товарами."""
        self.client.force_login(self.user)

        for url in self.get_protected_urls():
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_create_product(self):
        """Авторизованный пользователь может добавить товар."""
        self.client.force_login(self.user)

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
