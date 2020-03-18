from django.conf.urls import url

from proj import views

urlpatterns = [
    url(r'^$',                     views.proj_view,  name='proj_view'),
    url(r'^(?P<pk>\d+)/$',         views.proj_edit,  name='proj_edit'),
    url(r'^dirs/$',                views.dirs_view,  name='dirs_view'),
    url(r'^dirs/(?P<pk>\d+)/$',    views.dirs_edit,  name='dirs_edit'),
    url(r'^chg_dir/(?P<pk>\d+)/$', views.change_dir, name='change_dir'),
]
