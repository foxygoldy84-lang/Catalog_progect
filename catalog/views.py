<<<<<<< feature/catalog-setup
from django.shortcuts import render


def home_view(request):
    """Контроллер для отображения домашней страницы"""
    return render(request, "catalog/home.html")
=======
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from catalog.forms import ProductForm
from catalog.models import Category, ContactInfo, Product

# Количество товаров, выводимых на одной странице каталога
PRODUCTS_PER_PAGE = 6


def home_view(request):
    """Контроллер главной страницы."""
    # Выборка последних 5 созданных продуктов (сортируем по дате создания в обратном порядке)
    latest_products = Product.objects.all().order_by("-created_at")[:5]

    print("\n=== ПОСЛЕДНИЕ 5 ПРОДУКТОВ В КОНСОЛИ ===")
    for product in latest_products:
        print(f"ID: {product.id} | {product.name} | Цена: {product.price}")
    print("=======================================\n")

    # Все товары каталога для отображения списка карточек на главной странице
    products = Product.objects.select_related("category").order_by("-created_at", "-id")

    # Постраничный вывод товаров: пользователь может переходить между страницами
    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "catalog/home.html", {"page_obj": page_obj})


def product_detail_view(request, pk):
    """Контроллер страницы с подробной информацией о товаре."""
    product = get_object_or_404(Product.objects.select_related("category"), pk=pk)

    return render(request, "catalog/product_detail.html", {"product": product})
>>>>>>> local


def contacts_view(request):
    """Контроллер для страницы контактов с обработкой формы"""
    context = {}

    # Если пользователь нажал кнопку "Отправить" (метод POST)
    if request.method == "POST":
        # Забираем данные, которые ввел пользователь в поля name и message
        name = request.POST.get("name")
        message = request.POST.get("message")

        # Печатаем их прямо в консоль терминала PyCharm
        print("\n--- ПОЛУЧЕНО НОВОЕ СООБЩЕНИЕ ---")
        print(f"Имя пользователя: {name}")
        print(f"Текст сообщения: {message}")
        print("---------------------------------\n")

<<<<<<< feature/catalog-setup
        # Передаем информацию об успехе обратно на страницу
        context["success"] = True
        context["user_name"] = name

    return render(request, "catalog/contacts.html", context)
=======
    return render(request, "catalog/contacts.html", {"contact_data": contact_data})


def create_product_view(request):
    """Контроллер страницы добавления нового товара в каталог."""
    if request.method == "POST":
        # Если пользователь отправил данные, передаем их в форму (включая картинки request.FILES)
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Автоматически сохраняет новый товар в PostgreSQL!
            product = form.save()
            messages.success(
                request, f"Товар «{product.name}» успешно добавлен в каталог."
            )
            # После успешного добавления возвращаем на главную
            return redirect("catalog:home")
    else:
        # Если пользователь просто зашел на страницу, создаем пустую форму
        form = ProductForm()

    # Категории нужны для выпадающего списка в форме
    categories = Category.objects.all()

    return render(
        request,
        "catalog/product_form.html",
        {"form": form, "categories": categories},
    )
>>>>>>> local
