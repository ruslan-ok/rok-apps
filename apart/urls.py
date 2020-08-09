from django.urls import path
from . import v_apart, v_meter, v_bill, v_price

app_name = 'apart'
urlpatterns = [
    path('',                  v_apart.apart_list, name='apart_list'),
    path('<int:pk>/',         v_apart.apart_form, name='apart_form'),
    path('meters/',           v_meter.meter_list, name='meter_list'),
    path('meter/<int:pk>/',   v_meter.meter_form, name='meter_form'),
    path('bills/',            v_bill.bill_list,   name='bill_list'),
    path('bill/<int:pk>/',    v_bill.bill_form,   name='bill_form'),
    path('prices/',           v_price.price_list, name='price_list'),
    path('price/<int:pk>/',   v_price.price_form, name='price_form'),
    path('service/<int:pk>/', v_price.service,    name='service'),
]
