from django.urls import path
from photo.config import app_config
from photo import views

app_name = app_config['name']
urlpatterns = [
    path('',      views.FolderView.as_view(), name='list'),
    path('slider/',  views.PhotoView.as_view(),  name='detail'), # Форма для просмотра слайдера изображений
    path('image/',   views.get_photo, name='get_photo'), # Для отображения полноразмерного фото
    path('get_thumb/',         views.get_thumb, name='get_thumb'), # Для отображения миниатюры по имени файла
    path('get_mini/<int:pk>/', views.get_mini,  name='get_mini'),  # Для оторажения миниатюры на метке карты
]
