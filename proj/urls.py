from django.urls import path
from . import v_dirs, v_proj

app_name = 'proj'
urlpatterns = [
    path('',                   v_dirs.dirs_list, name='dirs_list'),
    path('<int:pk>/',          v_dirs.dirs_form, name='dirs_form'),
    path('expenses/',          v_proj.proj_list, name='proj_list'),
    path('expenses/<int:pk>/', v_proj.proj_form, name='proj_form'),
]
