from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
import views

urlpatterns = patterns('',
    url(r'^$',       views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url(r'^trip/',   include('trip.urls',   namespace="trip")),
    url(r'^fuel/',   include('fuel.urls',   namespace="fuel")),
    url(r'^apart/',  include('apart.urls',  namespace="apart")),
    url(r'^proj/',   include('proj.urls',   namespace="proj")),
    url(r'^task/',   include('task.urls',   namespace="task")),
    url(r'^pir/',    include('pir.urls',    namespace="pir")),
    url(r'^admin/',  include(admin.site.urls)),
)