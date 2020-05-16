from django.urls import path
from . import v_cars, v_fuel, v_part, v_repl

app_name = 'fuel'
urlpatterns = [
    path('refuel/parameters/',        v_cars.cars_list,     name='cars_list'),
    path('refuel/parameters/create/', v_cars.cars_add,      name='cars_add'),
    path('cars/<int:pk>/',            v_cars.cars_form,     name='cars_form'),
    path('cars/<int:pk>/delete/',     v_cars.cars_del,      name='cars_del'),
                                     
    path('refuel/',                   v_fuel.fuel_list,     name='fuel_list'),
    path('refuel/create/',            v_fuel.fuel_add,      name='fuel_add'),
    path('refuel/<int:pk>/',          v_fuel.fuel_form,     name='fuel_form'),
    path('refuel/<int:pk>/delete/',   v_fuel.fuel_del,      name='fuel_del'),
                                     
    path('part/',                     v_part.part_list,     name='part_list'),
    path('part/create/',              v_part.part_add,      name='part_add'),
    path('part/<int:pk>/',            v_part.part_form,     name='part_form'),
    path('part/<int:pk>/delete/',     v_part.part_del,      name='part_del'),
                                     
    path('replac/',                   v_repl.repl_list,     name='repl_list'),
    path('replac/create/',            v_repl.repl_add,      name='repl_add'),
    path('replac/<int:pk>/',          v_repl.repl_form,     name='repl_form'),
    path('replac/<int:pk>/delete/',   v_repl.repl_del,      name='repl_del'),
]
