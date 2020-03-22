from django.urls import path
from . import views

app_name = 'task'
urlpatterns = [
    path('',               views.task_view, name='task_view'),
    path('<int:pk>/',      views.task_edit, name='task_edit'),
    path('grps/',          views.grps_view, name='grps_view'),
    path('grps/<int:pk>/', views.grps_edit, name='grps_edit'),
    path('view/',          views.view_view, name='view_view'),
    path('view/<int:pk>/', views.view_edit, name='view_edit'),
    path('test/',          views.test_view, name='test_view'),
]
