from django.urls import path
from apart.views import apart, meter, price, bill
from task.const import APP_APART

app_name = APP_APART
urlpatterns = [
    path('', bill.ListView.as_view(), name='list'),
    path('<int:pk>/', bill.DetailView.as_view(), name='item'),
    path('meter/', meter.ListView.as_view(), name='meter-list'),
    path('meter/<int:pk>/', meter.DetailView.as_view(), name='meter-item'),
    path('price/', price.ListView.as_view(), name='price-list'),
    path('price/<int:pk>/', price.DetailView.as_view(), name='price-item'),
    path('apart/', apart.ListView.as_view(), name='apart-list'),
    path('apart/<int:pk>/', apart.DetailView.as_view(), name='apart-item'),
]
