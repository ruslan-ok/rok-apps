from django.conf.urls import url

from test import views

urlpatterns = [
    url(r'^$', views.test_view, name='test_view'),
]
