from django.shortcuts import render
from catalog.models import Product, ContactInfo


def home_view(request):
    """Контроллер главной страницы."""
    # Выборка последних 5 созданных продуктов (сортируем по дате создания в обратном порядке)
    latest_products = Product.objects.all().order_by("-created_at")[:5]

    print("\n=== ПОСЛЕДНИЕ 5 ПРОДУКТОВ В КОНСОЛИ ===")
    for product in latest_products:
        print(f"ID: {product.id} | {product.name} | Цена: {product.price}")
    print("=======================================\n")

    return render(request, "home.html")


def contacts_view(request):
    """Контроллер страницы контактов."""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        print(
            f"\n=== ДАННЫЕ ФОРМЫ ===\nИмя: {name}\nEmail: {email}\nСообщение: {message}\n====================\n"
        )

    # Получаем первую запись с контактами из админки (или None, если база пуста)
    contact_data = ContactInfo.objects.first()

    return render(request, "contacts.html", {"contact_data": contact_data})
