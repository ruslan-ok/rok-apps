from django.urls import path
from . import views

app_name = 'fuel'
urlpatterns = [
    path('',               views.index, name='index'),
    path('hello/',         views.hello, name='hello'),

    path('cars/',          views.cars,  name='cars'),
    path('cars/<int:pk>/', views.cars,  name='cars'),
    path('<int:pk>/',         views.fuel_edit,  name='fuel_edit'),
    path('part/',             views.part_view,  name='part_view'),
    path('part/<int:pk>/',    views.part_edit,  name='part_edit'),
    path('repl/<int:pt>/',    views.repl_view,  name='repl_view'),
    path('repl/<int:pt>/<int:pk>/', views.repl_edit,  name='repl_edit'),
    #path('cars/',             views.cars),
    #path('cars/<int:pk>/',    views.cars),
    path('chg_car/<int:pk>/', views.change_car, name='change_car'),
]
