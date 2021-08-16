#from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
#from django.views.i18n import JavaScriptCatalog
#from rest_framework import routers

from . import views
#from api import views_group as api_grp
#from api import views_task as api_task
#from api import views_step as api_step

#api_router = routers.DefaultRouter()
#api_router.register(r'groups', api_grp.GroupViewSet, basename='group')
#api_router.register(r'tasks', api_task.TaskViewSet, basename='task')
#api_router.register(r'steps', api_step.StepViewSet, basename='step')

urlpatterns = i18n_patterns(
    path('', views.index, name='index'),
    #path('todo/',   include('todo.urls')),
    path('note/',   include('note.urls')),
    path('account/', include('account.urls')),
    #path('admin/',   admin.site.urls, name='admin'),
    #path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    #path('api/', include(api_router.urls)),
    #path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))

    path('<int:pk>/completed/', views.toggle_completed, name='toggle-completed'),
    path('<int:pk>/important/', views.toggle_important, name='toggle-important'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
