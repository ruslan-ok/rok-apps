"""rusel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog

from . import views
from . import utils

urlpatterns = i18n_patterns(
    path('',            views.index,      name='index'),
    path('feedback/',   views.feedback,   name='feedback'),
    path('note/',       views.note,       name='note'),
    path('news/',       views.news,       name='news'),
    path('trash/',      views.trash,      name='trash'),

    path('etalon/',     utils.etalon,     name='etalon'),
    path('convert/',    utils.convert,    name='convert'),
    path('statistics/', utils.statistics, name='statistics'),

    path('check/', include('check.urls')),
    path('apart/', include('apart.urls')),
    path('fuel/',  include('fuel.urls')),
    path('proj/',  include('proj.urls')),
    path('trip/',  include('trip.urls')),
    path('wage/',  include('wage.urls')),
    path('todo/',  include('todo.urls')),
    path('pir/',   include('pir.urls')),
    path('store/', include('store.urls')),

    path('<int:folder_id>/',       include('hier.urls')),
    path('<int:folder_id>/note/',  include('note.urls')),

    path('account/', include('account.urls')),
    path('admin/',   admin.site.urls, name='admin'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('firebase-messaging-sw.js', views.ServiceWorkerView.as_view(), name='service_worker'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
