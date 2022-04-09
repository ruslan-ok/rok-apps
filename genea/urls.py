from django.urls import path
from photo.config import app_config
from genea import views

app_name = 'genea' # app_config['name']
urlpatterns = [
    path('', views.StemmaListView.as_view(), name='list'),
    path('<int:pk>/', views.export, name='export'),
    path('family/', views.chart_family, name='chart_family'),
    path('ancestors/', views.chart_ancestors, name='chart_ancestors'),
]
