from django.conf.urls import patterns, url

from task import views

urlpatterns = patterns('',
    url(r'^$',                  views.task_view, name='task_view'),
    url(r'^(?P<pk>\d+)/$',      views.task_edit, name='task_edit'),
    url(r'^grps/$',             views.grps_view, name='grps_view'),
    url(r'^grps/(?P<pk>\d+)/$', views.grps_edit, name='grps_edit'),
)
