from django.conf.urls import patterns, url

from apart import views

urlpatterns = patterns('',
    url(r'^$',                   views.apart_view, name='apart_view'),
    url(r'^(?P<per>\d+)/$',      views.apart_edit, name='apart_edit'),
    url(r'^tarif/$',             views.tarif_view, name='tarif_view'),
    url(r'^tarif/(?P<pk>\d+)/$', views.tarif_edit, name='tarif_edit'),
)
