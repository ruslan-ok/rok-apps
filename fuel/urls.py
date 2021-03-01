from django.urls import path
from . import views

app_name = 'fuel'
urlpatterns = [
    path('',           views.main,         name = 'main'),
    path('<int:pk>/',  views.item_form,    name = 'item_form'),
    path('cars/',      views.go_cars,      name = 'go_cars'),
    path('fuels/',     views.go_fuels,     name = 'go_fuels'),
    path('intervals/', views.go_intervals, name = 'go_intervals'),
    path('services/',  views.go_services,  name = 'go_services'),
    path('entity/<str:name>/<int:pk>/', views.fuel_entity, name = 'fuel_entity'),
]
