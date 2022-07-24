from django.urls import path
from backup.config import app_config
from backup import views

app_name = app_config['name']
urlpatterns = [
    path('', views.backup_check, name='list'),
]
