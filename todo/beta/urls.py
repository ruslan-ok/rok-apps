from django.urls import path
from todo.beta import views

app_name = 'todo_beta'
urlpatterns = [
    path('',          views.TaskListView.as_view(),   name = 'task-list'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name = 'task-detail'),
    path('<int:pk>/completed/', views.toggle_completed, name = 'toggle-completed'),
    path('<int:pk>/important/', views.toggle_important, name = 'toggle-important'),
]
