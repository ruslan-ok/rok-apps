from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('periods/', views.periods, name='periods'),
]
