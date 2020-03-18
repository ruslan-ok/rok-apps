from django.conf.urls import url

from task import views

urlpatterns = [
    url(r'^$',                  views.task_view, name='task_view'),
    url(r'^(?P<pk>\d+)/$',      views.task_edit, name='task_edit'),
    url(r'^grps/$',             views.grps_view, name='grps_view'),
    url(r'^grps/(?P<pk>\d+)/$', views.grps_edit, name='grps_edit'),
    url(r'^view/$',             views.view_view, name='view_view'),
    url(r'^view/(?P<pk>\d+)/$', views.view_edit, name='view_edit'),
    url(r'^test/$',             views.test_view, name='test_view'),
]
