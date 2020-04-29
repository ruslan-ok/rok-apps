from django.urls import path
from . import views

app_name = 'apart'
urlpatterns = [
    path('bills/',            views.bills_view,   name='bills_view'),
    path('bill/<int:per>/',   views.bill_edit,    name='bill_edit'),
    path('tariffs/',          views.tariffs_view, name='tariffs_view'),
    path('tariff/<int:pk>/',  views.tariff_edit,  name='tariff_edit'),
]
