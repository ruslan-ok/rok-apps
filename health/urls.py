from django.urls import path
from health.config import app_config
from health import views

app_name = app_config['name']
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('<int:pk>/', views.DetailView.as_view(), name='item'),
    path('incident/<int:pk>/', views.IncidentView.as_view(), name='group'),
]
