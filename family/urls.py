from django.urls import path
from family.config import app_config
from family.views import pedigree, diagram, individual, examine

app_name = app_config['name']
urlpatterns = [
    path('', diagram.diagram_start, name='list'),
    path('debug/', diagram.diagram_debug, name='debug'),
    path('<int:tree_id>/', diagram.diagram, name='diagram'),
    path('pedigree/', pedigree.PedigreeListView.as_view(), name='pedigree-list'),
    path('pedigree/import/', pedigree.import_tree, name='pedigree-import'),
    path('pedigree/<int:pk>/', pedigree.PedigreeDetailsView.as_view(), name='pedigree-detail'),
    path('pedigree/<int:pk>/export/', pedigree.export_tree, name='pedigree-export'),
    path('pedigree/<int:pk>/export/file/', pedigree.get_gedcom_file, name='pedigree-file'),
    path('pedigree/<int:pk>/examine/', examine.examine_tree, name='pedigree-examine'),
    path('pedigree/<int:ft>/individual/<str:pk>/<str:view>', individual.IndividualDetailsView.as_view(), name='individual-detail'),
    path('<str:role>/<int:pk>/doc/<str:fname>', pedigree.get_doc, name='doc'),
]
