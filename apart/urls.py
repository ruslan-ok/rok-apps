from django.urls import path
from . import v_apart, v_meter, v_bill, v_price

app_name = 'apart'
urlpatterns = [
    path('aparts/',                v_apart.apart_list, name='apart_list'),
    path('aparts/create/',         v_apart.apart_add,  name='apart_add'),
    path('apart/<int:pk>/',        v_apart.apart_form, name='apart_form'),
    path('apart/<int:pk>/delete/', v_apart.apart_del,  name='apart_del'),

    path('meters/',                v_meter.meter_list, name='meter_list'),
    path('meters/create/',         v_meter.meter_add,  name='meter_add'),
    path('meter/<int:pk>/',        v_meter.meter_form, name='meter_form'),
    path('meter/<int:pk>/delete/', v_meter.meter_del,  name='meter_del'),

    path('bills/',                 v_bill.bill_list,   name='bill_list'),
    path('bills/create/',          v_bill.bill_add,    name='bill_add'),
    path('bill/<int:pk>/',         v_bill.bill_form,   name='bill_form'),
    path('bill/<int:pk>/delete/',  v_bill.bill_del,    name='bill_del'),

    path('prices/',                v_price.price_list, name='price_list'),
    path('prices/create/',         v_price.price_add,  name='price_add'),
    path('price/<int:pk>/',        v_price.price_form, name='price_form'),
    path('price/<int:pk>/delete/', v_price.price_del,  name='price_del'),
]
