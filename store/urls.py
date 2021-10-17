from django.urls import path
from store.config import app_config
from store import views

app_name = app_config['name']
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('group/<int:pk>/', views.GroupView.as_view(), name='group'),
    path('<int:pk>/', views.DetailView.as_view(), name='item'),
    path('<int:pk>/doc/<str:fname>', views.get_doc, name='doc'),
]
