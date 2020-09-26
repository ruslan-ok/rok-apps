from django.urls import path
from . import views

app_name = 'news'
urlpatterns = [
    path('',                       views.news_list,    name='news_list'),
    path('<int:pk>/',              views.news_form,    name='news_form'),
    path('all/',                   views.all_news,     name='all_news'),
    path('list/<int:pk>/',         views.list_news,    name='list_news'),
    path('list_article/<int:pk>/', views.news_list_form,    name='news_list_form'),
    path('group/<int:pk>/',        views.news_group_form,   name='news_group_form'),
    path('toggle_group/<int:pk>/', views.news_toggle_group, name='news_toggle_group'),
    path('docs/<str:name>',        views.news_get_doc,      name='news_get_doc'),
]
