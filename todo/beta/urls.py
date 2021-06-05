from django.urls import path
from todo.beta import views

app_name = 'todo_beta'
urlpatterns = [
    path('myday/',              views.MyDayListView.as_view(),       name = 'myday-list'),
    path('myday/<int:pk>/',     views.MyDayDetailView.as_view(),     name = 'myday-detail'),
    path('important/',          views.ImportantListView.as_view(),   name = 'important-list'),
    path('important/<int:pk>/', views.ImportantDetailView.as_view(), name = 'important-detail'),
    path('planned/',            views.PlannedListView.as_view(),     name = 'planned-list'),
    path('planned/<int:pk>/',   views.PlannedDetailView.as_view(),   name = 'planned-detail'),
    path('',                    views.AllListView.as_view(),         name = 'all-list'),
    path('<int:pk>/',           views.AllDetailView.as_view(),       name = 'all-detail'),
    path('completed/',          views.CompletedListView.as_view(),   name = 'completed-list'),
    path('completed/<int:pk>/', views.CompletedDetailView.as_view(), name = 'completed-detail'),
    path('bygroup/<int:grp>/',          views.ByGroupListView.as_view(),       name = 'bygroup-list'),
    path('bygroup/<int:grp>/<int:pk>/', views.ByGroupDetailView.as_view(),     name = 'bygroup-detail'),
]
