from django.urls import path
from health.config import app_config
from health.views import incident, marker

app_name = app_config['name']
urlpatterns = [
    path('', marker.ListView.as_view(), name='list'),
    path('<int:pk>/', marker.DetailView.as_view(), name='item'),

    path('incident/', incident.ListView.as_view(), name='incident-list'),
    path('incident/<int:pk>/', incident.DetailView.as_view(), name='incident-item'),
    path('incident/<int:pk>/doc/<str:fname>', incident.get_doc, name='incident-doc'),
]
