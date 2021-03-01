from django.urls import path
from . import views

app_name = 'note'
urlpatterns = [
    path('',                       views.note_list,         name='note_list'),
    path('<int:pk>/',              views.note_form,         name='note_form'),
    path('entity/<str:name>/<int:pk>/', views.note_entity,  name='note_entity'),
    path('all/',                   views.all_notes,         name='all_notes'),
    path('list/<int:pk>/',         views.list_notes,        name='list_notes'),
    path('list_form/<int:pk>/',    views.note_list_form,    name='note_list_form'),
    path('group/<int:pk>/',        views.note_group_form,   name='note_group_form'),
    path('toggle_group/<int:pk>/', views.note_toggle_group, name='note_toggle_group'),
    path('doc/<str:name>',         views.note_get_doc,      name='note_get_doc'),
]
