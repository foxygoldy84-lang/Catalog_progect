from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from blog.models import BlogPost


class BlogPostViewTests(TestCase):
    """Проверки CRUD и дополнительной логики блога."""

    @classmethod
    def setUpTestData(cls):
        cls.published_post = BlogPost.objects.create(
            title="Опубликованная статья",
            content="Содержимое опубликованной статьи",
            is_published=True,
        )
        cls.draft_post = BlogPost.objects.create(
            title="Черновик",
            content="Содержимое черновика",
            is_published=False,
        )

    def test_list_shows_only_published_posts(self):
        """В списке статей выводятся только опубликованные записи."""
        response = self.client.get(reverse("blog:blogpost_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_post.title)
        self.assertNotContains(response, self.draft_post.title)

    def test_detail_increments_views_count(self):
        """Открытие статьи увеличивает счётчик просмотров."""
        url = reverse("blog:blogpost_detail", args=[self.published_post.pk])

        self.client.get(url)
        self.client.get(url)

        self.published_post.refresh_from_db()
        self.assertEqual(self.published_post.views_count, 2)

    def test_create_post(self):
        """Новая статья сохраняется в базе."""
        response = self.client.post(
            reverse("blog:blogpost_create"),
            {
                "title": "Новая статья",
                "content": "Текст новой статьи",
                "is_published": "on",
            },
        )

        post = BlogPost.objects.get(title="Новая статья")
        self.assertRedirects(response, reverse("blog:blogpost_detail", args=[post.pk]))
        self.assertTrue(post.is_published)

    def test_update_redirects_to_detail(self):
        """После редактирования пользователь попадает на просмотр статьи."""
        url = reverse("blog:blogpost_update", args=[self.published_post.pk])

        response = self.client.post(
            url,
            {
                "title": "Обновлённая статья",
                "content": "Обновлённый текст",
                "is_published": "on",
            },
        )

        self.assertRedirects(
            response,
            reverse("blog:blogpost_detail", args=[self.published_post.pk]),
        )
        self.published_post.refresh_from_db()
        self.assertEqual(self.published_post.title, "Обновлённая статья")

    def test_delete_post(self):
        """Статью можно удалить."""
        url = reverse("blog:blogpost_delete", args=[self.published_post.pk])

        response = self.client.post(url)

        self.assertRedirects(response, reverse("blog:blogpost_list"))
        self.assertFalse(BlogPost.objects.filter(pk=self.published_post.pk).exists())

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_congratulation_email_is_sent_at_100_views(self):
        """При достижении 100 просмотров отправляется письмо."""
        self.published_post.views_count = 99
        self.published_post.save(update_fields=["views_count"])

        self.client.get(reverse("blog:blogpost_detail", args=[self.published_post.pk]))

        self.published_post.refresh_from_db()
        self.assertEqual(self.published_post.views_count, 100)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("100 просмотров", mail.outbox[0].subject)
