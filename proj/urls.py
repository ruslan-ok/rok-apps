from django.urls import path
from . import v_dirs, v_proj

app_name = 'proj'
urlpatterns = [
    path('proj/parameters/',        v_dirs.dirs_list, name='dirs_list'),
    path('proj/parameters/create/', v_dirs.dirs_add,  name='dirs_add'),
    path('dirs/<int:pk>/',          v_dirs.dirs_form, name='dirs_form'),
    path('dirs/<int:pk>/delete/',   v_dirs.dirs_del,  name='dirs_del'),
                                   
    path('proj/',                   v_proj.proj_list, name='proj_list'),
    path('proj/create/',            v_proj.proj_add,  name='proj_add'),
    path('proj/<int:pk>/',          v_proj.proj_form, name='proj_form'),
    path('proj/<int:pk>/delete/',   v_proj.proj_del,  name='proj_del'),
]
