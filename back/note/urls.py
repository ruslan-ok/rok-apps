from django.urls import path

from note import views
from task.const import APP_NOTE

app_name = APP_NOTE
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('group/<int:pk>/', views.GroupView.as_view(), name='group'),
    path('<int:pk>/', views.DetailView.as_view(), name='item'),
]
