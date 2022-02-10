from django.urls import path
from photo.config import app_config
from photo import views

app_name = app_config['name']
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
]
