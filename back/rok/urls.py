"""
URL configuration for rok project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from rest_framework import routers

from api.views import group as api_grp
from api.views import task as api_task
from api.views import step as api_step
from api.views import urls as api_urls
from api.views import profile as api_profile
from api.views import logs as api_logs
from api.views import famtree as api_family
from api.views import widget as api_widget
from api.views import service as api_service
from api.views import visited as api_visited
from api.views import core as api_core
from cram.api import views as api_cram
from apart.api import views as api_apart
from react.api import views as api_react

api_router = routers.DefaultRouter()
api_router.register('groups', api_grp.GroupViewSet, basename='group')
api_router.register('tasks', api_task.TaskViewSet, basename='task')
api_router.register('steps', api_step.StepViewSet, basename='step')
api_router.register('urls', api_urls.UrlsViewSet, basename='urls')
api_router.register('profile', api_profile.ProfileViewSet, basename='profile')
api_router.register('logs', api_logs.LogsViewSet, basename='logs')
api_router.register('famtree', api_family.FamTreeViewSet, basename='famtree')
api_router.register('apart/estate', api_apart.ApartView, basename='apart')
api_router.register('apart/property/meter', api_apart.ApartMeterView, basename='apart-meter')
api_router.register('apart/property/service', api_apart.ApartServiceView, basename='apart-service')
api_router.register('apart/period/meter', api_apart.PeriodMetersView, basename='period-meter')
api_router.register('apart/period/meter_value', api_apart.MeterValueView, basename='meter-value')
api_router.register('apart/period/service', api_apart.PeriodServicesView, basename='period-service')
api_router.register('apart/period/service_amount', api_apart.ServiceAmountView, basename='service-amount')
api_router.register('cram/lang', api_cram.CramLangViewSet, basename='cram-lang')
api_router.register('cram/group', api_cram.CramGroupViewSet, basename='cram-group')
api_router.register('cram/phrase', api_cram.CramPhraseViewSet, basename='cram-phrase')
api_router.register('cram/lang_phrase', api_cram.CramLangPhraseViewSet, basename='cram-lang-phrase')
api_router.register('visited', api_visited.VisitedViewSet, basename='visited')

from core import app_doc
#api_router = routers.DefaultRouter()

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('manifest.json', TemplateView.as_view(template_name='manifest.json')),
    path('asset-manifest.json', TemplateView.as_view(template_name='asset-manifest.json')),
    path('favicon.ico', RedirectView.as_view(url='static/favicon.ico')),
    path('firebase-messaging-sw.js', TemplateView.as_view(template_name='firebase-messaging-sw.js', content_type='text/javascript')),

    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('bill/', include('apart.urls')),
    path('cram/', include('cram.urls')),
    path('docs/', include('docs.urls')),
    path('expen/', include('expen.urls')),
    path('family/', include('family.urls')),
    path('fuel/', include('fuel.urls')),
    path('health/', include('health.urls')),
    path('logs/', include('logs.urls')),
    path('news/', include('news.urls')),
    path('note/', include('note.urls')),
    path('photo/', include('photo.urls')),
    path('store/', include('store.urls')),
    path('todo/', include('todo.urls')),
    path('warr/', include('warr.urls')),
    path('api/', include(api_router.urls)),
    path('assets/<str:file>/', api_react.get_assets),

    path('api/react/header/', api_react.header),
    path('api/react/main_page/', api_react.main_page),
    path('api/react/get_username/', api_react.get_username),

    path('api/get_chart_data/', api_widget.get_chart_data_api, name='get_chart_data'),
    path('api/core/get_exchange_rate/', api_core.get_exchange_rate, name='get_exchange_rate'),
    path('api/get_dir/', api_service.get_dir, name='get_dir'),
    path('api/modify_mt/', api_service.modify_mt, name='modify_mt'),
    path('api/exchange_rate_update/', api_service.exchange_rate_update, name='exchange_rate_update'),    
    
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('<str:role>/<int:pk>/doc/<str:fname>', app_doc.get_app_doc, name='doc'),
    path('<str:role>/<int:pk>/thumbnail/<str:fname>', app_doc.get_app_thumbnail, name='thumbnail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

