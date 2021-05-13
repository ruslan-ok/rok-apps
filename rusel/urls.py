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

router.register(r'drf/myday', todo_views.MyDayViewSet, basename='todo-myday')
router.register(r'drf/important', todo_views.ImportantViewSet, basename='todo-important')
router.register(r'drf/planned', todo_views.PlannedViewSet, basename='todo-planned')
router.register(r'drf/todo', todo_views.AllViewSet, basename='atask')
router.register(r'drf/completed', todo_views.CompletedViewSet, basename='todo-completed')
router.register(r'drf/list/(?P<list_pk>[^/.]+)', todo_views.ByListViewSet, basename='todo-list')

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
    path('store/',  include('store.urls')),
    path('note/',   include('note.urls')),
    path('news/',   include('note.urls_news')),
    path('photo/',  include('photo.urls')),
    path('health/', include('health.urls')),

    path('<int:folder_id>/',       include('hier.urls')),

    path('account/', include('account.urls')),
    path('admin/',   admin.site.urls, name='admin'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
