from django.urls import path
from todo.beta import views

app_name = 'todo_beta'
urlpatterns = [
    path('',          views.TaskListView.as_view(),   name = 'task-list'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name = 'task-detail'),
]
