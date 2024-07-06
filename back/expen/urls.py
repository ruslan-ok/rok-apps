from django.urls import path

from expen import views
from task.const import APP_EXPEN

app_name = APP_EXPEN
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('<int:pk>/', views.DetailView.as_view(), name='item'),
    path('project/<int:pk>/', views.ProjectView.as_view(), name='group'),
]
