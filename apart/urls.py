from django.urls import path
from . import views

app_name = 'apart'
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
]
