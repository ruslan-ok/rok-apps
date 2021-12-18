from django.urls import path
from apart.config import app_config
from apart.views import serv, meter, price, bill

app_name = app_config['name']
urlpatterns = [
    path('', meter.ListView.as_view(), name='list'),
    path('<int:pk>/', meter.DetailView.as_view(), name='item'),
    path('<int:pk>/doc/<str:fname>', meter.get_doc, name='doc'),
    path(app_config['group_entity'] + '/<int:pk>/', meter.ApartView.as_view(), name='group'),

    path('service/', serv.ListView.as_view(), name='service-list'),
    path('service/<int:pk>/', serv.DetailView.as_view(), name='service-item'),
    path('service/<int:pk>/doc/<str:fname>', serv.get_doc, name='service-doc'),

    path('price/', price.ListView.as_view(), name='price-list'),
    path('price/<int:pk>/', price.DetailView.as_view(), name='price-item'),
    path('price/<int:pk>/doc/<str:fname>', price.get_doc, name='price-doc'),

    path('bill/', bill.ListView.as_view(), name='bill-list'),
    path('bill/<int:pk>/', bill.DetailView.as_view(), name='bill-item'),
    path('bill/<int:pk>/doc/<str:fname>', bill.get_doc, name='bill-doc'),
]
