from django.urls import path
from . import views

app_name = 'wage'
urlpatterns = [
    path('', views.index, name='index'),
    path('periods/', views.periods, name='periods'),
]
