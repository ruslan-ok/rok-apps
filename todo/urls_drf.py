from django.urls import path
from . import views_drf as views

app_name = 'todo_drf'
urlpatterns = [
    path('', views.TodoAllViewSet.as_view({'get': 'list'}), name='todo-list'),
    path('<int:pk>/', views.TodoAllViewSet.as_view({'get': 'retrieve'}), name='todo-detail'),
    path('myday/', views.TodoMydayViewSet.as_view({'get': 'list'}), name='todo-list'),
    path('myday/<int:pk>/', views.TodoMydayViewSet.as_view({'get': 'retrieve'}), name='todo-detail'),
]
