from django.urls import path
from trip.config import app_config
from trip import views

app_name = app_config['name']
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('<int:pk>/', views.DetailView.as_view(), name='item'),
    path('<int:pk>/doc/<str:fname>', views.get_doc, name='doc'),
    path(app_config['group_entity'] + '/<int:pk>/', views.PersonView.as_view(), name='group'),
]
