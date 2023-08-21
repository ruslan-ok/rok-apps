from django.urls import path
from fuel.config import app_config
from fuel.views import fuel, part, serv, car

app_name = app_config['name']
urlpatterns = [
    path('', fuel.ListView.as_view(), name='list'),
    path('<int:pk>/', fuel.DetailView.as_view(), name='item'),
    path('part/', part.ListView.as_view(), name='part-list'),
    path('part/<int:pk>/', part.DetailView.as_view(), name='part-item'),
    path('service/', serv.ListView.as_view(), name='service-list'),
    path('service/<int:pk>/', serv.DetailView.as_view(), name='service-item'),
    path('car/', car.ListView.as_view(), name='car-list'),
    path('car/<int:pk>/', car.DetailView.as_view(), name='car-item'),
]
