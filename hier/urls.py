from django.urls import path
from . import views

app_name = 'hier'
urlpatterns = [
    path('',                       views.index,       name='index'),
]
