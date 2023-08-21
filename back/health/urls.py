from django.urls import path
from health.config import app_config
from health.views import incident, marker, chart

app_name = app_config['name']
urlpatterns = [
    path('', marker.ListView.as_view(), name='list'),
    path('<int:pk>/', marker.DetailView.as_view(), name='item'),

    path('incident/', incident.ListView.as_view(), name='incident-list'),
    path('incident/<int:pk>/', incident.DetailView.as_view(), name='incident-item'),

    path('weight/', chart.WeightView.as_view(), name='chart-weight'),
    path('waist/', chart.WaistView.as_view(), name='chart-waist'),
    path('temp/', chart.TempView.as_view(), name='chart-temp'),
]
