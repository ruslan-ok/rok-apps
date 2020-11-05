from django.urls import path
from . import views

app_name = 'photo'
urlpatterns = [
    path('', views.main, name = 'main'),
    path('all/', views.all, name = 'all'),
    path('map/', views.map, name = 'map'),

    path('show/', views.show, name = 'show'),
    path('edit/', views.edit, name = 'edit'),
    path('edit_id/<int:pk>/', views.edit_id, name = 'edit_id'),
    path('mini/<int:pk>/', views.mini, name = 'mini'),
    path('photo/<int:pk>/', views.photo, name = 'photo'),
    path('goto/', views.goto, name = 'goto'),
    path('level/<int:level>/', views.jump, name = 'jump'),
]
