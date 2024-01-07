from django.urls import path
from logs.config import app_config
from logs import views

app_name = app_config['name']
urlpatterns = [
    path('', views.log_view, name='list'),
    path('<str:location>/<int:pk>/', views.LogEventView.as_view(), name='detail'),
]
