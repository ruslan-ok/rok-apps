from django.urls import path
from docs.config import app_config
from docs import views

app_name = app_config['name']
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
]
