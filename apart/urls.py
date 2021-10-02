from django.urls import path
from apart.config import app_config
from apart.views import apart, serv, meter, price, bill

app_name = app_config['name']
urlpatterns = [
    path('', apart.ListView.as_view(), name='list'),
    path('<int:pk>/', apart.DetailView.as_view(), name='item'),
    path('<int:pk>/doc/<str:fname>', apart.get_doc, name='doc'),

    path('service/', serv.ListView.as_view(), name='service-list'),
    path('service/<int:pk>/', serv.DetailView.as_view(), name='service-item'),
    path('service/<int:pk>/doc/<str:fname>', serv.get_doc, name='service-doc'),

    path('meter/', meter.ListView.as_view(), name='meter-list'),
    path('meter/<int:pk>/', meter.DetailView.as_view(), name='meter-item'),
    path('meter/<int:pk>/doc/<str:fname>', meter.get_doc, name='meter-doc'),

    path('price/', price.ListView.as_view(), name='price-list'),
    path('price/<int:pk>/', price.DetailView.as_view(), name='price-item'),
    path('price/<int:pk>/doc/<str:fname>', price.get_doc, name='price-doc'),

    path('bill/', bill.ListView.as_view(), name='bill-list'),
    path('bill/<int:pk>/', bill.DetailView.as_view(), name='bill-item'),
    path('bill/<int:pk>/doc/<str:fname>', bill.get_doc, name='bill-doc'),
]
