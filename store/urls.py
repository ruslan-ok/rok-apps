from django.urls import path
from . import views

app_name = 'store'
urlpatterns = [
    path('parameters/', views.entry_param, name='entry_param'),
    path('clear/',      views.clear,       name='clear'),
    path('import/',     views.xml_import,  name='xml_import'),
                                                            
    path('',                         views.entry_list, name='entry_list'),
    path('create/',                  views.entry_add,  name='entry_add'),
    path('<int:content_id>/',        views.entry_form, name='entry_form'),
    path('<int:content_id>/delete/', views.entry_del,  name='entry_del'),
    path('<int:content_id>/move/<int:to_folder>/', views.entry_move, name='entry_move'),
]
