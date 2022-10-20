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
    path('people/', views.IndiListView.as_view(), name='people'),
    path('person/<int:pk>/', views.IndiDetailsView.as_view(), name='person'),
    path('person/<int:pk>/avatar/', views.avatar, name='avatar'),
    path('families/', views.FamListView.as_view(), name='families'),
    path('family/<int:pk>/', views.FamDetailsView.as_view(), name='family'),
    path('media/', views.MediaListView.as_view(), name='media'),
]
