from django.urls import path
from photo.config import app_config
from photo import views

app_name = app_config['name']
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('<int:pk>/', views.DetailView.as_view(), name='item'),
    path(app_config['group_entity'] + '/<int:pk>/', views.FolderView.as_view(), name='group'),
]