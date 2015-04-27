from django.conf.urls import patterns, url

from fuel import views

urlpatterns = patterns('',
    url(r'^$',                     views.fuel_view,  name='fuel_view'),
    url(r'^(?P<pk>\d+)/$',         views.fuel_edit,  name='fuel_edit'),
    url(r'^part/$',                views.part_view,  name='part_view'),
    url(r'^part/(?P<pk>\d+)/$',    views.part_edit,  name='part_edit'),
    url(r'^repl/(?P<pt>\d+)/$',    views.repl_view,  name='repl_view'),
    url(r'^repl/(?P<pt>\d+)/(?P<pk>\d+)/$', views.repl_edit,  name='repl_edit'),
    url(r'^cars/$',                views.cars_view,  name='cars_view'),
    url(r'^cars/(?P<pk>\d+)/$',    views.cars_edit,  name='cars_edit'),
    url(r'^chg_car/(?P<pk>\d+)/$', views.change_car, name='change_car'),
)
