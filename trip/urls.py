from django.conf.urls import patterns, url

from trip import views

urlpatterns = patterns('',
    url(r'^$',                  views.trip_view,  name='trip_view'),
    url(r'^(?P<pk>\d+)/$',      views.trip_edit,  name='trip_edit'),
    url(r'^count/$',            views.trip_count, name='trip_count'),
    url(r'^pers/$',             views.pers_view,  name='pers_view'),
    url(r'^pers/(?P<pk>\d+)/$', views.pers_edit,  name='pers_edit'),
)
