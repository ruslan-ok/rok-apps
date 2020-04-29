from django.urls import path
from . import views

app_name = 'hier'
urlpatterns = [
    path('toggle/',               views.toggle,        name='toggle'),
    path('',                      views.folder_list,   name='folder_list'),
    path('down/',                 views.folder_down,   name='folder_down'),
    path('dir/',                  views.folder_dir,    name='folder_dir'),
    path('properties/',           views.folder_form,   name='folder_form'),
    path('create/',               views.folder_add,    name='folder_add'),
    path('properties/delete/',    views.folder_del,    name='folder_del'),
    path('move/<int:to_folder>/', views.folder_move,   name='folder_move'),
    path('dir/parameters/',       views.folder_param,  name='folder_param'),
]
