from django.db import models


class BlogPost(models.Model):
    """Модель блоговой записи."""

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    preview = models.ImageField(
        upload_to="blog/previews/",
        blank=True,
        null=True,
        verbose_name="Превью",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=False, verbose_name="Признак публикации")
    views_count = models.PositiveIntegerField(
        default=0, verbose_name="Количество просмотров"
    )

    class Meta:
        verbose_name = "Блоговая запись"
        verbose_name_plural = "Блоговые записи"
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title
