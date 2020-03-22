from django.urls import path
from . import views

app_name = 'proj'
urlpatterns = [
    path('',                  views.proj_view,  name='proj_view'),
    path('<int:pk>/',         views.proj_edit,  name='proj_edit'),
    path('dirs/',             views.dirs_view,  name='dirs_view'),
    path('dirs/<int:pk>/',    views.dirs_edit,  name='dirs_edit'),
    path('chg_dir/<int:pk>/', views.change_dir, name='change_dir'),
]
