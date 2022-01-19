#from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog
from rest_framework import routers

from . import views
from api import views_group as api_grp
from api import views_task as api_task
from api import views_step as api_step
from api import views_urls as api_urls
from api import views_profile as api_profile

api_router = routers.DefaultRouter()
api_router.register(r'groups', api_grp.GroupViewSet, basename='group')
api_router.register(r'tasks', api_task.TaskViewSet, basename='task')
api_router.register(r'steps', api_step.StepViewSet, basename='step')
api_router.register(r'urls', api_urls.UrlsViewSet, basename='urls')
api_router.register(r'profile', api_profile.ProfileViewSet, basename='profile')

urlpatterns = i18n_patterns(
    path('', views.ListView.as_view(), name='index'),
    path('todo/',   include('todo.urls')),
    path('note/',   include('note.urls')),
    path('news/',   include('news.urls')),
    path('apart/',  include('apart.urls')),
    path('docs/',   include('docs.urls')),
    path('store/',  include('store.urls')),
    path('expen/',  include('expen.urls')),
    path('fuel/',   include('fuel.urls')),
    path('health/', include('health.urls')),
    path('warr/',   include('warr.urls')),
    path('v3_photo/',  include('photo.urls')),
    path('account/', include('account.urls')),
    #path('admin/',   admin.site.urls, name='admin'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('api/', include(api_router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('v2_apart/',  include('v2_apart.urls')),
    path('v2_fuel/',   include('v2_fuel.urls')),
    path('v2_proj/',   include('v2_proj.urls')),
    path('trip/',      include('v2_trip.urls')),
    path('work/',      include('v2_wage.urls')),
    path('v2_todo/',   include('v2_todo.urls')),
    path('v2_store/',  include('v2_store.urls')),
    path('v2_note/',   include('v2_note.urls')),
    path('v2_news/',   include('v2_note.urls_news')),
    path('photo/',     include('v2_photo.urls')),
    path('v2_health/', include('v2_health.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
