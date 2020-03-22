from django.urls import path
from . import views

app_name = 'pir'
urlpatterns = [
    path('<int:tbl>/', views.pir_edit,  name='pir_edit'),
]
