from django.urls import path
from genea.config import app_config
from genea import views

app_name = app_config['name']
urlpatterns = [
    path('', views.pedigree, name='list'),
    path('refresh/', views.refresh, name='refresh'),
    path('no_data/', views.no_data, name='no_data'),
]
