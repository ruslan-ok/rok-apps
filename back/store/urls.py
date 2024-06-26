from django.urls import path

from store import views
from task.const import APP_STORE

app_name = APP_STORE
urlpatterns = [
    path('', views.ListView.as_view(), name='list'),
    path('group/<int:pk>', views.GroupView.as_view(), name='group'),
    path('<int:pk>', views.DetailView.as_view(), name='item'),
    path('params', views.params, name='params'),
]
