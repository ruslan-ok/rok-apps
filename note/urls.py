from django.urls import path
from . import views

app_name = 'note'
urlpatterns = [
    path('',                              views.note_list,   name='note_list'),
    path('down/',                         views.note_down,   name='note_down'),
    path('create/',                       views.note_add,    name='note_add'),
    path('<int:content_id>/',             views.note_form,   name='note_form'),
    path('<int:content_id>/delete/',      views.note_del,    name='note_del'),
    path('<int:content_id>/move/<int:to_folder>/', views.note_move, name='note_move'),

    path('news/',                         views.news_list,   name='news_list'),
    path('news/<int:content_id>/',        views.news_form,   name='news_form'),
    path('news/create/',                  views.news_add,    name='news_add'),
    path('news/<int:content_id>/delete/', views.news_del,    name='news_del'),
]
