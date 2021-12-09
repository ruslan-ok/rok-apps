from django.urls import path
from expen.config import app_config
from expen.views import project, expense

app_name = app_config['name']
urlpatterns = [
    path('', project.ListView.as_view(), name='list'),
    path('group/<int:pk>/', project.GroupView.as_view(), name='group'),
    path('<int:pk>/', project.DetailView.as_view(), name='item'),
    path('<int:pk>/doc/<str:fname>', project.get_doc, name='doc'),

    path('expense/', expense.ListView.as_view(), name='expense-list'),
    path('expense/<int:pk>/', expense.DetailView.as_view(), name='expense-item'),
    path('expense/<int:pk>/doc/<str:fname>', expense.get_doc, name='expense-doc'),
]
