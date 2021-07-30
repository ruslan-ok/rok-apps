from django.urls import path
from . import views
from . import fcm

app_name = 'todo'
urlpatterns = [
    path('',          views.TaskListView.as_view(),   name = 'task-list'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name = 'task-detail'),
    path('group/<int:pk>/', views.TaskGroupDetailView.as_view(), name = 'group-detail'),
    path('<int:pk>/completed/', views.toggle_completed, name = 'toggle-completed'),
    path('<int:pk>/important/', views.toggle_important, name = 'toggle-important'),

    path('fcm/',                    fcm.fcm,             name = 'fcm'),
    path('fcm_add/',                fcm.fcm_add,         name = 'fcm_add'),
    path('fcm_del/',                fcm.fcm_del,         name = 'fcm_del'),
    path('postpone/<int:pk>/',      fcm.fcm_postpone,    name = 'fcm_postpone'),
    path('done/<int:pk>/',          fcm.fcm_done,        name = 'fcm_done'),
]
