from django.urls import path
from cram.config import app_config
from cram import views

app_name = app_config['name']
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('<int:pk>/', views.DetailView.as_view(), name='item'),
    path('training/', views.training, name='training'),
    path('group/<int:pk>/', views.GroupView.as_view(), name='group'),
]
