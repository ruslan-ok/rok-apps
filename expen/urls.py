from django.urls import path
from expen.config import app_config
from expen import views

app_name = app_config['name']
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('<int:pk>/', views.DetailView.as_view(), name='item'),
    path('<int:pk>/doc/<str:fname>', views.get_doc, name='doc'),
    path(app_config['group_entity'] + '/<int:pk>/', views.ProjectView.as_view(), name='group'),
]
