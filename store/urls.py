from django.urls import path
from . import views

app_name = 'store'
urlpatterns = [
    path('',          views.entry_list, name='entry_list'),
    path('<int:pk>/', views.entry_form, name='entry_form'),
    path('actual/',   views.actual,     name='actual'),
    path('waste/',    views.waste,      name='waste'),
    path('all/',      views.all,        name='all'),
    path('params/',   views.param_list, name='param_list'),

    path('list/<int:pk>/',         views.list_items,   name='list_items'),
    path('list_article/<int:pk>/', views.list_form,    name='list_form'),
    path('group/<int:pk>/',        views.group_form,   name='group_form'),
    path('toggle_group/<int:pk>/', views.toggle_group, name='toggle_group'),
]
