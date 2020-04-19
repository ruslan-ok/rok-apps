from django.urls import path
from . import views

app_name = 'note'
urlpatterns = [
    path('',                      views.index,       name='index'),
    path('view_set/<int:pk>/',    views.view_set,    name='view_set'),

    path('lists/',                views.list_list,   name='list_list'),
    path('list/create/',          views.list_add,    name='list_add'),
    path('list/<int:pk>/',        views.list_form,   name='list_form'),
    path('list/<int:pk>/delete/', views.list_del,    name='list_del'),

    path('note/create/',          views.note_add,    name='note_add'),
    path('note/<int:pk>/',        views.note_form,   name='note_form'),
    path('note/<int:pk>/delete/', views.note_del,    name='note_del'),

    path('views/',                views.view_list,   name='view_list'),
    path('view/create/',          views.view_add,    name='view_add'),
    path('view/<int:vw>/',        views.view_form,   name='view_form'),
    path('view/<int:vw>/delete/', views.view_del,    name='view_del'),

    path('view/<int:vw>/list/<int:lst>/add/', views.view_list_add, name='view_list_add'),
    path('view/<int:vw>/list/<int:lst>/del/', views.view_list_del, name='view_list_del'),

    path('chrono/create/',          views.chrono_add,  name='chrono_add'),
    path('chrono/<int:pk>/',        views.chrono_form, name='chrono_form'),
    path('chrono/<int:pk>/delete/', views.chrono_del,  name='chrono_del'),
]
