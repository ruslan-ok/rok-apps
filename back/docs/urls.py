from django.urls import path
from docs import views

app_name = 'docs'
urlpatterns = [
    path('', views.FolderView.as_view(), name='list'),
    path('file/', views.get_file, name='doc'),
]
