from django.urls import include, path
from rest_framework import routers

from api.views import auth
from api.views import login
from api.views import main_page
from api.views import header
from api.views import fixed
from api.views import chart
from api.views import toggle
from api.views import page_config
from api.views import groups
from api.views import todo
from api.views import weight

api_router = routers.DefaultRouter()
api_router.register('group', groups.GroupViewSet, basename='group')
api_router.register('todo', todo.TodoViewSet, basename='task')
api_router.register('weight', weight.WeightViewSet, basename='weight')

urlpatterns = [
    path('auth/', auth.auth),
    path('demo/', auth.demo),
    path('csrf_setup/', login.csrf_setup),
    path('login/', login.LoginView.as_view()),
    path('logout/', auth.logout),
    path('main_page/', main_page.main_page),
    path('config/', page_config.PageConfigView.as_view()),
    path('header/', header.header),
    path('fixed/', fixed.fixed),
    path('chart/', chart.chart),
    path('group/<int:pk>/toggle_sub_group/', toggle.toggle_sub_group),
    path('todo/<int:pk>/extra/', todo.extra),

    path('', include(api_router.urls)),
]
