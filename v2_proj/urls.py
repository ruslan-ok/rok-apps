from django.urls import path
from . import views

app_name = 'v2_proj'
urlpatterns = [
    path('',          views.main,        name = 'main'),
    path('<int:pk>/', views.item_form,   name = 'item_form'),
    path('projects/', views.go_projects, name = 'go_projects'),
    path('expenses/', views.go_expenses, name = 'go_expenses'),
    path('entity/<str:name>/<int:pk>/', views.proj_entity, name = 'proj_entity'),
]
