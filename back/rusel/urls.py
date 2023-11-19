from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog
from django.views.generic import RedirectView
from rest_framework import routers

from . import views, views_old
from api.views import group as api_grp
from api.views import task as api_task
from api.views import step as api_step
from api.views import urls as api_urls
from api.views import profile as api_profile
from api.views import logs as api_logs
from api.views import famtree as api_family
from api.views import widget as api_widget
from api.views import service as api_service
from cram.api import views as api_cram
from apart.api import views as api_apart
from react.api import views as api_react

api_router = routers.DefaultRouter()
api_router.register(r'groups', api_grp.GroupViewSet, basename='group')
api_router.register(r'tasks', api_task.TaskViewSet, basename='task')
api_router.register(r'steps', api_step.StepViewSet, basename='step')
api_router.register(r'urls', api_urls.UrlsViewSet, basename='urls')
api_router.register(r'profile', api_profile.ProfileViewSet, basename='profile')
api_router.register(r'logs', api_logs.LogsViewSet, basename='logs')
api_router.register(r'famtree', api_family.FamTreeViewSet, basename='famtree')
api_router.register(r'apart/estate', api_apart.ApartView, basename='apart')
api_router.register(r'apart/property/meter', api_apart.ApartMeterView, basename='apart-meter')
api_router.register(r'apart/property/service', api_apart.ApartServiceView, basename='apart-service')
api_router.register(r'apart/period/meter', api_apart.PeriodMetersView, basename='period-meter')
api_router.register(r'apart/period/meter_value', api_apart.MeterValueView, basename='meter-value')
api_router.register(r'apart/period/service', api_apart.PeriodServicesView, basename='period-service')
api_router.register(r'apart/period/service_amount', api_apart.ServiceAmountView, basename='service-amount')
api_router.register(r'cram/lang', api_cram.CramLangViewSet, basename='cram-lang')
api_router.register(r'cram/group', api_cram.CramGroupViewSet, basename='cram-group')
api_router.register(r'cram/phrase', api_cram.CramPhraseViewSet, basename='cram-phrase')
api_router.register(r'cram/lang_phrase', api_cram.CramLangPhraseViewSet, basename='cram-lang-phrase')

urlpatterns = i18n_patterns(
    path('', views.index, name='index'),
    path('account/',include('account.urls')),
    path('bill/',   include('apart.urls')),
    path('cram/',   include('cram.urls')),
    path('docs/',   include('docs.urls')),
    path('expen/',  include('expen.urls')),
    path('family/', include('family.urls')),
    path('fuel/',   include('fuel.urls')),
    path('health/', include('health.urls')),
    path('news/',   include('news.urls')),
    path('note/',   include('note.urls')),
    path('photo/',  include('photo.urls')),
    path('store/',  include('store.urls')),
    path('todo/',   include('todo.urls')),
    path('warr/',   include('warr.urls')),
    path('logs/',   include('logs.urls')),
    path('admin/',  admin.site.urls, name='admin'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('api/',    include(api_router.urls)),

    path('assets/<str:file>', api_react.get_assets),
    path('api/react/header', api_react.header),
    path('api/react/main_page', api_react.main_page),
    path('api/react/demo', api_react.demo),
    path('api/react/login', api_react.login),
    path('api/react/logout', api_react.logout),
    path('api/react/get_username', api_react.get_username),

    path('api/get_widget/', api_widget.get_widget, name='get_widget'),
    path('api/get_chart_data/', api_widget.get_chart_data, name='get_chart_data'),
    path('api/get_dir/', api_service.get_dir, name='get_dir'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('<str:role>/<int:pk>/doc/<str:fname>', views_old.get_doc, name='doc'),
    path('<str:role>/<int:pk>/thumbnail/<str:fname>', views_old.get_thumbnail, name='thumbnail'),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
