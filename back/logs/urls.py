from django.urls import path
from task.const import APP_LOGS
from logs import views

app_name = APP_LOGS
urlpatterns = [
    path('', views.log_view, name='list'),
]
