from django.urls import path
from . import views

app_name = 'v2_apart'
urlpatterns = [
    path('',                 views.main,     name = 'main'),
    path('<int:pk>/',        views.item,     name = 'item'),
    path('aparts/',          views.aparts,   name = 'aparts'),
    path('services/',        views.services, name = 'services'),
    path('meters/',          views.meters,   name = 'meters'),
    path('prices/',          views.prices,   name = 'prices'),
    path('bills/',           views.bills,    name = 'bills'),
    path('toggle/<int:pk>/', views.toggle,   name = 'toggle'),
    path('doc/<str:name>',   views.doc,      name = 'doc'),
    path('entity/<str:name>/<int:pk>/', views.apart_entity, name = 'apart_entity'),
]
