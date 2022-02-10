from django.urls import path
from . import views

app_name = 'v2_photo'
urlpatterns = [
    # Режимы приложения
    path('',     views.main, name = 'main'), # Фотографии в виде миниатюр
    path('main', views.main, name = 'main'), # Фотографии в виде миниатюр
    path('map/', views.map,  name = 'map'),  # Фотографии на карте
    path('one/', views.one,  name = 'one'),  # Просмотр одной фотографии, заданной именем файла

    # Навигация
    path('by_id/<int:pk>/',   views.by_id, name = 'by_id'), # Просмотр фотографии с указанным id
    path('form/',             views.form,  name = 'form'),  # Отображение формы
    path('goto/',             views.goto,  name = 'goto'),  # Опуститься в указанную папку
    path('rise/<int:level>/', views.rise,  name = 'rise'),  # Подняться на указанный уровень вверх

    # Служебные адреса для отображения фото
    path('get_photo/<int:pk>/', views.get_photo, name = 'get_photo'), # Для отображения полноразмерного фото
    path('get_thumb/',          views.get_thumb, name = 'get_thumb'), # Для отображения миниатюры по имени файла
    path('get_mini/<int:pk>/',  views.get_mini,  name = 'get_mini'),  # Для оторажения миниатюры на метке карты
]
