from django.urls import path
from . import views, convert

app_name = 'note'
urlpatterns = [
    path('',                       views.note_list,    name='note_list'),
    path('<int:pk>/',              views.note_form,    name='note_form'),
    path('all/',                   views.all_notes,    name='all_notes'),
    path('list/<int:pk>/',         views.list_notes,   name='list_notes'),
    path('list_article/<int:pk>/', views.note_list_form,    name='note_list_form'),
    path('group/<int:pk>/',        views.note_group_form,   name='note_group_form'),
    path('toggle_group/<int:pk>/', views.note_toggle_group, name='note_toggle_group'),
    path('docs/<str:name>',        views.note_get_doc,      name='note_get_doc'),

    path('convert/', convert.convert, name='convert'),
]
