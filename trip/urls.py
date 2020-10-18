from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('',          views.main,       name='main'),
    path('<int:pk>/', views.item_form,  name='item_form'),
    path('persons/',  views.go_persons, name='go_persons'),
    path('trips/',    views.go_trips,   name='go_trips'),
]
