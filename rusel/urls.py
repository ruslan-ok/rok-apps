from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog
from rest_framework import routers

from . import views
from task import views as task_views
from todo import views_drf as todo_views

router = routers.DefaultRouter()
router.register(r'groups', task_views.TaskGrpSimpleViewSet, basename='taskgrp')
router.register(r'tasks', todo_views.TodoAllViewSet, basename='atask')

urlpatterns = i18n_patterns(
    path('', views.index, name='index'),
    path('move/', views.move, name='move'),
    path('switch/', views.switch, name='switch'),

    path('apart/',  include('apart.urls')),
    path('fuel/',   include('fuel.urls')),
    path('proj/',   include('proj.urls')),
    path('trip/',   include('trip.urls')),
    path('wage/',   include('wage.urls')),
    path('todo/',   include('todo.urls')),
    path('drf/todo/', include('todo.urls_drf')),
    path('store/',  include('store.urls')),
    path('note/',   include('note.urls')),
    path('news/',   include('note.urls_news')),
    path('photo/',  include('photo.urls')),
    path('health/', include('health.urls')),

    path('<int:folder_id>/',       include('hier.urls')),

    path('account/', include('account.urls')),
    path('admin/',   admin.site.urls, name='admin'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    path('new/task/', task_views.ATaskViewSet.as_view({'get': 'list'}), name='atask-list'),
    path('new/task/<int:pk>/', task_views.ATaskViewSet.as_view({'get': 'retrieve'}), name='atask-detail'),
    path('new/note/', task_views.NoteViewSet.as_view({'get': 'list'}), name='note-list'),
    path('new/note/<int:pk>/', task_views.NoteViewSet.as_view({'get': 'retrieve'}), name='note-detail'),
    path('new/news/', task_views.NewsViewSet.as_view({'get': 'list'}), name='news-list'),
    path('new/news/<int:pk>/', task_views.NewsViewSet.as_view({'get': 'retrieve'}), name='news-detail'),

    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
