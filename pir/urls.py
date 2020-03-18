from django.conf.urls import url

from pir import views

urlpatterns = [
    url(r'^(?P<tbl>\w+)/$', views.pir_edit,  name='pir_edit'),
]
