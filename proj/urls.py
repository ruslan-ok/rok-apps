from django.urls import path
from . import views

app_name = 'proj'
urlpatterns = [
    path('',                          views.proj_list,  name='proj_list'),
    path('<int:content_id>/',         views.proj_form,  name='proj_form'),
    path('dirs/',                     views.dirs_list,  name='dirs_list'),
    path('dirs/<int:content_id>/',    views.dirs_form,  name='dirs_form'),
    path('chg_dir/<int:content_id>/', views.change_dir, name='change_dir'),
]
