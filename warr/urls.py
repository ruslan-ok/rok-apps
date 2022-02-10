from django.urls import path
from warr.config import app_config
from warr import views

app_name = app_config['name']
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('<int:pk>/', views.DetailView.as_view(), name='item'),
    path('group/<int:pk>/', views.GroupView.as_view(), name='group'),
]
