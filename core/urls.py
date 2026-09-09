from django.contrib import admin
from django.urls import path
from catalog import views


urlpatterns = [
    # 1. Админка
    path('admin/', admin.site.urls),

    # 2. Главная страница (теперь через views.home_view)
    path('', views.home_view, name='home'),

    # 3. Страница контактов (теперь через views.contacts_view)
    path('contacts/', views.contacts_view, name='contacts'),
]
