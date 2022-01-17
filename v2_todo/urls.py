from django.urls import path
from . import views
from . import fcm

app_name = 'v2_todo'
urlpatterns = [
    path('',                        views.task_list,     name = 'task_list'),
    path('all/',                    views.all_tasks,     name = 'all_tasks'),
    path('myday/',                  views.myday,         name = 'myday'),
    path('important/',              views.important,     name = 'important'),
    path('planned/',                views.planned,       name = 'planned'),
    path('completed/',              views.completed,     name = 'completed'),
    path('list/<int:pk>/',          views.list_items,    name = 'list_items'),
    path('<int:pk>/',               views.task_form,     name = 'task_form'),
    path('entity/<str:name>/<int:pk>/', views.todo_entity, name = 'todo_entity'),

    path('list_form/<int:pk>/',     views.list_form,     name = 'list_form'),
    path('group/<int:pk>/',         views.group_form,    name = 'group_form'),
    path('toggle_group/<int:pk>/',  views.toggle_group,  name = 'toggle_group'),
    path('toggle/<int:pk>/',        views.period_toggle, name = 'period_toggle'),
    path('doc/<str:name>',          views.task_get_doc,  name = 'task_get_doc'),

    path('fcm/',                    fcm.fcm,             name = 'fcm'),
    path('fcm_add/',                fcm.fcm_add,         name = 'fcm_add'),
    path('fcm_del/',                fcm.fcm_del,         name = 'fcm_del'),
    path('postpone/<int:pk>/',      fcm.fcm_postpone,    name = 'fcm_postpone'),
    path('done/<int:pk>/',          fcm.fcm_done,        name = 'fcm_done'),
]