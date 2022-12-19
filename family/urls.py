from django.urls import path
from family.config import app_config
from family.views import pedigree, diagram

app_name = app_config['name']
urlpatterns = [
    path('', pedigree.PedigreeListView.as_view(), name='list'),
    path('<int:pk>/', pedigree.PedigreeDetailsView.as_view(), name='pedigree-detail'),
    path('diagram/', diagram.diagram, name='diagram'),
]
