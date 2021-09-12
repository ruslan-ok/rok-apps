from django.urls import path
from todo.const import app_name
from . import views
from . import fcm

app_name = app_name
urlpatterns = [
    path('', views.TodoListView.as_view(), name='todo-list'),
    path('group/<int:pk>/', views.TodoGroupDetailView.as_view(), name='group-detail'),
    path('<int:pk>/', views.TodoDetailView.as_view(), name='item-detail'),
    path('<int:pk>/doc/<str:fname>', views.get_doc, name='get_doc'),

    path('fcm/',                    fcm.fcm,             name = 'fcm'),
    path('fcm_add/',                fcm.fcm_add,         name = 'fcm_add'),
    path('fcm_del/',                fcm.fcm_del,         name = 'fcm_del'),
    path('postpone/<int:pk>/',      fcm.fcm_postpone,    name = 'fcm_postpone'),
    path('done/<int:pk>/',          fcm.fcm_done,        name = 'fcm_done'),
]
