from django.urls import path
from . import views
from . import fcm

app_name = 'todo'
urlpatterns = [
    path('',                        views.task_list,     name = 'task_list'),
    path('all/',                    views.all_tasks,     name = 'all_tasks'),
    path('mayday/',                 views.myday,         name = 'myday'),
    path('important/',              views.important,     name = 'important'),
    path('planned/',                views.planned,       name = 'planned'),
    path('completed/',              views.completed,     name = 'completed'),
    path('list_items/<int:pk>/',    views.list_items,    name = 'list_items'),
    path('task/<int:pk>/',          views.task_form,     name = 'task_form'),
    path('list/<int:pk>/',          views.list_form,     name = 'list_form'),
    path('group/<int:pk>/',         views.group_form,    name = 'group_form'),
    path('group_toggle/<int:pk>/',  views.group_toggle,  name = 'group_toggle'),
    path('period_toggle/<int:pk>/', views.period_toggle, name = 'period_toggle'),
    path('fcm/',                    fcm.fcm,             name = 'fcm'),
    path('fcm_check/',              fcm.fcm_check,       name = 'fcm_check'),
    path('fcm_add/',                fcm.fcm_add,         name = 'fcm_add'),
    path('fcm_del/',                fcm.fcm_del,         name = 'fcm_del'),
    path('fcm_send/<int:pk>/',      fcm.fcm_send,        name = 'fcm_send'),
    path('fcm_test/',               fcm.fcm_test,        name = 'fcm_test'),
    path('postpone/<int:pk>/',      fcm.fcm_postpone,    name = 'fcm_postpone'),
    path('done/<int:pk>/',          fcm.fcm_done,        name = 'fcm_done'),
]
