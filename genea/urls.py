from django.urls import path
from photo.config import app_config
from genea import views

app_name = app_config['name']
urlpatterns = [
    path('', views.test, name='test'),
]
