from django.urls import path
from docs.config import app_config
from docs import views

app_name = app_config['name']
urlpatterns = [
    path('', views.FolderView.as_view(), name='list'),
    path('file/', views.get_file, name='doc'),
]
