from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog
from rest_framework import routers

from . import views
from api import views_group as api_grp
from api import views_task as api_task

api_router = routers.DefaultRouter()
api_router.register(r'groups', api_grp.GroupViewSet, basename='group')
api_router.register(r'tasks', api_task.TaskViewSet, basename='task')

urlpatterns = i18n_patterns(
    path('', views.index, name='index'),
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

    path('beta/todo/', include('todo.beta.urls')),

    path('account/', include('account.urls')),
    path('admin/',   admin.site.urls, name='admin'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    path('api/', include(api_router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
