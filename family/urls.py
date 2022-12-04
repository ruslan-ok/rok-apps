from django.urls import path
from family.config import app_config
from family import views

app_name = app_config['name']
urlpatterns = [
    path('', views.tree, name='list'),
    path('<int:pk>/', views.FamTreeDetailsView.as_view(), name='famtree-details'),
    path('<int:pk>/photo/', views.photo, name='photo'),
    path('<int:pk>/thumbnail/', views.thumbnail, name='thumbnail'),
    path('<int:pk>/thumbnail_100/', views.thumbnail_100, name='thumbnail_100'),
    path('pedigree/', views.PedigreeListView.as_view(), name='pedigree'),
    path('calendar/', views.CalendarListView.as_view(), name='calendar'),
    path('individual/', views.IndiListView.as_view(), name='individuals'),
    path('individual/<int:pk>/', views.IndiDetailsView.as_view(), name='individual'),
    path('individual/<int:pk>/avatar/', views.avatar, name='avatar'),
    path('family/', views.FamListView.as_view(), name='families'),
    path('family/<int:pk>/', views.FamDetailsView.as_view(), name='family'),
    path('notes/', views.NotesListView.as_view(), name='notes'),
    path('media/', views.MediaListView.as_view(), name='media'),
    path('reports/', views.ReportsListView.as_view(), name='reports'),
]
