from django.conf.urls import patterns, url

from pir import views

urlpatterns = patterns('',
    url(r'^(?P<tbl>\w+)/$', views.pir_edit,  name='pir_edit'),
)
