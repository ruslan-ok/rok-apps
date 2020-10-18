from django.urls import path
from . import views

app_name = 'wage'
urlpatterns = [
    path('', views.main, name = 'main'),
    path('periods/', views.periods, name = 'periods'),
    path('employees/', views.employees, name = 'employees'),
    path('departments/', views.departments, name = 'departments'),
    path('posts/', views.posts, name = 'posts'),
    path('pay_titles/', views.pay_titles, name = 'pay_titles'),
    path('toggle/<int:pk>/', views.toggle, name = 'toggle'),
    path('<int:pk>/', views.item_form, name = 'item_form'),
    path('list_form/<int:pk>/', views.item2_form, name = 'item2_form'),

    path('total/', views.total, name = 'total'),
    path('accrual/', views.accrual, name = 'accrual'),
    path('payment/', views.payment, name = 'payment'),
    path('appoint/', views.appoint, name = 'appoint'),
    path('education/', views.education, name = 'education'),
    path('surname/', views.surname, name = 'surname'),
    path('child/', views.child, name = 'child'),
    path('dep_hist/', views.dep_hist, name = 'dep_hist'),
    path('dep_info/', views.dep_info, name = 'dep_info'),
]
