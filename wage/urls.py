from django.urls import path
from . import views

app_name = 'wage'
urlpatterns = [
    path('', views.index, name='index'),
    path('tree/<int:pk>/', views.tree, name='tree'),
    #path('depart/<pk>/', views.depart, name='depart'),
    path('depart/<int:pk>/', views.DepartDetailView.as_view(), name='depart'),
    path('employee/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee'),
    #path('employee/<int:pk>/', views.employee, name='employee'),
    path('clear/', views.clear, name='clear'),
    path('import/', views.xml_import, name='xml_import'),
]
