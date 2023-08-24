from django.urls import path
from react import views

urlpatterns = [
    path('', views.index, name='react_index'),
    path('currency/', views.index, name='react_currency'),
]
