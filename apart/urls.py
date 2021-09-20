from django.urls import path
from apart.config import app_config
from apart.views import apart, serv, meter, price, bill

app_name = app_config['name']
urlpatterns = [
    path('', apart.ListView.as_view(), name='list'),
    path('<int:pk>/', apart.DetailView.as_view(), name='item'),
    path('<int:pk>/doc/<str:fname>', apart.DetailView.get_doc, name='doc'),

    path('services/', serv.ListView.as_view(), name='serv-list'),
    path('services/<int:pk>/', serv.DetailView.as_view(), name='serv-item'),
    path('services/<int:pk>/doc/<str:fname>', serv.DetailView.get_doc, name='serv-doc'),

    path('meters/', meter.ListView.as_view(), name='meter-list'),
    path('meters/<int:pk>/', meter.DetailView.as_view(), name='meter-item'),
    path('meters/<int:pk>/doc/<str:fname>', meter.DetailView.get_doc, name='meter-doc'),

    path('prices/', price.ListView.as_view(), name='price-list'),
    path('prices/<int:pk>/', price.DetailView.as_view(), name='price-item'),
    path('prices/<int:pk>/doc/<str:fname>', price.DetailView.get_doc, name='price-doc'),

    path('bills/', bill.ListView.as_view(), name='bill-list'),
    path('bills/<int:pk>/', bill.DetailView.as_view(), name='bill-item'),
    path('bills/<int:pk>/doc/<str:fname>', bill.DetailView.get_doc, name='bill-doc'),
]
