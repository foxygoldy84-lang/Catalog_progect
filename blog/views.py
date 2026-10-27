from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.models import BlogPost

# Количество записей блога на одной странице
BLOG_POSTS_PER_PAGE = 6

# Количество просмотров, при котором отправляется поздравление
CONGRATULATIONS_VIEWS = 100


class BlogPostListView(ListView):
    """Список опубликованных блоговых записей."""

    model = BlogPost
    template_name = "blog/blogpost_list.html"
    context_object_name = "posts"
    paginate_by = BLOG_POSTS_PER_PAGE

    def get_queryset(self):
        # На странице списка показываем только опубликованные записи
        return BlogPost.objects.filter(is_published=True)


class BlogPostDetailView(DetailView):
    """Страница отдельной блоговой записи."""

    model = BlogPost
    template_name = "blog/blogpost_detail.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        post = super().get_object(queryset)

        # Увеличиваем счётчик просмотров при открытии статьи
        BlogPost.objects.filter(pk=post.pk).update(views_count=F("views_count") + 1)
        post.refresh_from_db(fields=["views_count"])

        if post.views_count == CONGRATULATIONS_VIEWS:
            self._send_congratulations(post)

        return post

    @staticmethod
    def _send_congratulations(post):
        """Отправляет поздравление, когда статья достигла 100 просмотров."""
        send_mail(
            subject=f"Статья «{post.title}» набрала 100 просмотров!",
            message=(
                f"Поздравляем! Ваша статья «{post.title}» достигла "
                f"{CONGRATULATIONS_VIEWS} просмотров.\n\n"
                "Продолжайте публиковать качественный контент!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.BLOG_NOTIFICATION_EMAIL],
            fail_silently=True,
        )


class BlogPostCreateView(CreateView):
    """Создание новой блоговой записи."""

    model = BlogPost
    fields = ("title", "content", "preview", "is_published")
    template_name = "blog/blogpost_form.html"

    def get_success_url(self):
        return reverse("blog:blogpost_detail", kwargs={"pk": self.object.pk})


class BlogPostUpdateView(UpdateView):
    """Редактирование блоговой записи."""

    model = BlogPost
    fields = ("title", "content", "preview", "is_published")
    template_name = "blog/blogpost_form.html"

    def get_success_url(self):
        # После успешного редактирования переходим на просмотр статьи
        return reverse("blog:blogpost_detail", kwargs={"pk": self.object.pk})


class BlogPostDeleteView(DeleteView):
    """Удаление блоговой записи."""

    model = BlogPost
    template_name = "blog/blogpost_confirm_delete.html"
    success_url = reverse_lazy("blog:blogpost_list")
