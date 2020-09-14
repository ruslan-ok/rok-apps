from django.urls import path
from . import v_car, v_interval, v_fueling, v_service

app_name = 'fuel'
urlpatterns = [
    path('cars/', v_car.car_list, name = 'car_list'),
    path('car/<int:pk>/', v_car.car_form, name = 'car_form'),
    path('intervals/', v_interval.interval_list, name = 'interval_list'),
    path('interval/<int:pk>/', v_interval.interval_form, name = 'interval_form'),
    path('', v_fueling.fueling_list, name = 'fueling_list'),
    path('<int:pk>/', v_fueling.fueling_form, name = 'fueling_form'),
    path('services/', v_service.service_list, name = 'service_list'),
    path('service/<int:pk>/', v_service.service_form, name = 'service_form'),
]
