from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 2. Главная страница (подключает созданный файл home.html)
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # 3. Страница контактов (подключает созданный файл contacts.html)
    path('contacts/', TemplateView.as_view(template_name='contacts.html'), name='contacts'),
]
