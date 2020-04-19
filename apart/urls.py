from django.urls import path
from . import views

app_name = 'apart'
urlpatterns = [
    path('',                views.apart_view, name='index'),
    path('<int:per>/',      views.apart_edit, name='apart_edit'),
    path('tarif/',          views.tarif_view, name='tarif_view'),
    path('tarif/<int:pk>/', views.tarif_edit, name='tarif_edit'),
]
