from django.shortcuts import render


def home_view(request):
    """Контроллер для отображения домашней страницы"""
    return render(request, "catalog/home.html")


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

        # Передаем информацию об успехе обратно на страницу
        context["success"] = True
        context["user_name"] = name

    return render(request, "catalog/contacts.html", context)
