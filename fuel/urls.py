from django.urls import path
from . import views

app_name = 'fuel'
urlpatterns = [
    path('fuel/',                           views.fuel_list,  name='fuel_list'),
    path('fuel/<int:content_id>/',          views.fuel_form,  name='fuel_form'),

    path('part/',                           views.part_list,  name='part_list'),
    path('part/<int:content_id>/',          views.part_form,  name='part_form'),
    
    path('repl/<int:content_id>/',          views.repl_list,  name='repl_list'),
    path('repl/<int:pt>/<int:content_id>/', views.repl_form,  name='repl_form'),
    
    path('cars/',                           views.cars_list,  name='cars_list'),

    path('cars/<int:content_id>/',          views.cars_form,  name='cars_form'),
    path('chg_car/<int:content_id>/',       views.change_car, name='change_car'),
]
