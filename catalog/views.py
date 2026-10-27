from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from catalog.forms import ProductForm
from catalog.models import Category, Product

# Количество товаров, выводимых на одной странице каталога
PRODUCTS_PER_PAGE = 6


class HomeView(ListView):
    """Контроллер главной страницы с постраничным списком товаров."""

    model = Product
    template_name = "catalog/home.html"
    paginate_by = PRODUCTS_PER_PAGE

    def get_queryset(self):
        return Product.objects.select_related("category").order_by("-created_at", "-id")

    def paginate_queryset(self, queryset, page_size):
        """Некорректный номер страницы не должен приводить к ошибке 404."""
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        page_number = self.request.GET.get(self.page_kwarg) or 1
        page = paginator.get_page(page_number)
        return paginator, page, page.object_list, page.has_other_pages()


class ProductDetailView(DetailView):
    """Контроллер страницы с подробной информацией о товаре."""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.select_related("category")


class ContactsView(TemplateView):
    """Контроллер страницы контактов с обработкой формы."""

    template_name = "catalog/contacts.html"

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        message = request.POST.get("message")

        # Печатаем данные формы в консоль терминала
        print("\n--- ПОЛУЧЕНО НОВОЕ СООБЩЕНИЕ ---")
        print(f"Имя пользователя: {name}")
        print(f"Текст сообщения: {message}")
        print("---------------------------------\n")

        context = self.get_context_data(success=True, user_name=name)
        return self.render_to_response(context)


class ProductFormContextMixin:
    """Добавляет список категорий в контекст формы продукта."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class ProductCreateView(ProductFormContextMixin, CreateView):
    """Контроллер страницы добавления нового товара в каталог."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Товар «{self.object.name}» успешно добавлен в каталог.",
        )
        return response


class ProductUpdateView(ProductFormContextMixin, UpdateView):
    """Контроллер страницы редактирования товара."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def get_success_url(self):
        return reverse("catalog:product_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Товар «{self.object.name}» успешно обновлён.",
        )
        return response


class ProductDeleteView(DeleteView):
    """Контроллер страницы удаления товара."""

    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:home")

    def form_valid(self, form):
        product_name = self.get_object().name
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Товар «{product_name}» успешно удалён.",
        )
        return response
