from django.urls import include, path
from rest_framework import routers

from api.views import auth
from api.views import main_page
from api.views import env
from api.views import header
from api.views import fixed
from api.views import chart
from api.views import toggle
from api.views import todo_extra
from api.views import groups
from api.views import todo

api_router = routers.DefaultRouter()
api_router.register('group', groups.GroupViewSet, basename='group')
api_router.register('todo', todo.TodoViewSet, basename='task')

urlpatterns = [
    path('auth/', auth.auth),
    path('demo/', auth.demo),
    path('login/', auth.login),
    path('logout/', auth.logout),
    path('main_page/', main_page.main_page),
    path('env/', env.env),
    path('header/', header.header),
    path('fixed/', fixed.fixed),
    path('chart/', chart.chart),
    path('groups_test/', groups.groups_test),
    path('group/<int:pk>/toggle_sub_group/', toggle.toggle_sub_group),
    path('todo/<int:pk>/extra/', todo_extra.extra),
    path('todo/<int:pk>/completed/', todo_extra.completed),
    path('todo/<int:pk>/important/', todo_extra.important),

    path('', include(api_router.urls)),
]
