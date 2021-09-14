from django.urls import path
from todo.config import app_config
from . import views
from . import fcm

app_name = app_config['name']
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('group/<int:pk>/', views.GroupView.as_view(), name='group'),
    path('<int:pk>/', views.DetailView.as_view(), name='item'),
    path('<int:pk>/doc/<str:fname>', views.DetailView.get_doc, name='doc'),

    path('fcm/',                    fcm.fcm,             name = 'fcm'),
    path('fcm_add/',                fcm.fcm_add,         name = 'fcm_add'),
    path('fcm_del/',                fcm.fcm_del,         name = 'fcm_del'),
    path('postpone/<int:pk>/',      fcm.fcm_postpone,    name = 'fcm_postpone'),
    path('done/<int:pk>/',          fcm.fcm_done,        name = 'fcm_done'),
]
