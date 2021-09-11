from django.urls import path
from todo.const import app_name
from . import views

app_name = app_name
urlpatterns = [
    path('', views.TodoListView.as_view(), name='todo-list'),
    path('group/<int:pk>/', views.TodoGroupDetailView.as_view(), name='group-detail'),
    path('<int:pk>/', views.TodoDetailView.as_view(), name='item-detail'),
    path('<int:pk>/doc/<str:fname>', views.get_doc, name='get_doc'),
]
