from django.urls import path
from . import views

app_name = 'note'
urlpatterns = [
    path('', views.NoteListView.as_view(), name='note-list'),
    path('group/<int:pk>/', views.NoteGroupDetailView.as_view(), name='group-detail'),
    path('<int:pk>/', views.NoteDetailView.as_view(), name='item-detail'),
    path('<int:pk>/doc/<str:fname>', views.get_doc, name='get_doc'),
]
