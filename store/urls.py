from django.urls import path
from . import views

app_name = 'store'
urlpatterns = [
    path('',            views.index,      name='index'),
    path('parameters/', views.param_form, name='param_form'),
    path('clear/',      views.clear,      name='clear'),
    path('import/',     views.xml_import, name='xml_import'),
                                                            
    path('groups/',                views.group_list, name='group_list'),
    path('group/create/',          views.group_add,  name='group_add'),
    path('group/<int:pk>/',        views.group_form, name='group_form'),
    path('group/<int:pk>/delete/', views.group_del,  name='group_del'),
                                                            
    path('entry/create/',          views.entry_add,  name='entry_add'),
    path('entry/<int:pk>/',        views.entry_form, name='entry_form'),
    path('entry/<int:pk>/delete/', views.entry_del,  name='entry_del'),
]
