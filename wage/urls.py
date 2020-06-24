from django.urls import path
from . import views

app_name = 'wage'
urlpatterns = [
    path('',                              views.index,          name='index'),
    path('tree/<int:pk>/',                views.tree,           name='tree'),
    path('clear/',                        views.clear,          name='clear'),
    path('import/',                       views.xml_import,     name='xml_import'),
                                                            
    path('departments/',                  views.depart_list,    name='depart_list'),
    path('departments/create/',           views.depart_add,     name='depart_add'),
    path('department/<int:pk>/',          views.depart_form,    name='depart_form'),
    path('department/<int:pk>/delete/',   views.depart_del,     name='depart_del'),
                                                              
    path('department/<int:dep>/history/create/',          views.dep_hist_add,   name='dep_hist_add'),
    path('department/<int:dep>/history/<int:pk>/',        views.dep_hist_form,  name='dep_hist_form'),
    path('department/<int:dep>/history/<int:pk>/delete/', views.dep_hist_del,   name='dep_hist_del'),
                                         
    path('posts/',                        views.post_list,      name='post_list'),
    path('posts/create/',                 views.post_add,       name='post_add'),
    path('post/<int:pk>/',                views.post_form,      name='post_form'),
    path('post/<int:pk>/delete/',         views.post_del,       name='post_del'),

    path('pay_titles/',                   views.pay_title_list, name='pay_title_list'),
    path('pay_titles/create/',            views.pay_title_add,  name='pay_title_add'),
    path('pay_title/<int:pk>/',           views.pay_title_form, name='pay_title_form'),
    path('pay_title/<int:pk>/delete/',    views.pay_title_del,  name='pay_title_del'),
                                       
    path('periods/',                      views.period_list,    name='period_list'),
    path('periods/create/',               views.period_add,     name='period_add'),
    path('period/<int:pk>/',              views.period_form,    name='period_form'),
    path('period/<int:pk>/delete/',       views.period_del,     name='period_del'),
    
    path('employees/',                    views.empl_list,      name='empl_list'),
    path('employees/create/',             views.empl_add,       name='empl_add'),
    path('employee/<int:pk>/',            views.empl_form,      name='empl_form'),
    path('employee/<int:pk>/delete/',     views.empl_del,       name='empl_del'),

    path('employee/<int:empl>/appoints/',                  views.appoint_list,   name='appoint_list'),
    path('employee/<int:empl>/appoints/create/',           views.appoint_add,    name='appoint_add'),
    path('employee/<int:empl>/appoint/<int:pk>/',          views.appoint_form,   name='appoint_form'),
    path('employee/<int:empl>/appoint/<int:pk>/delete/',   views.appoint_del,    name='appoint_del'),
                                         
    path('employee/<int:empl>/educations/',                views.education_list, name='education_list'),
    path('employee/<int:empl>/educations/create/',         views.education_add,  name='education_add'),
    path('employee/<int:empl>/education/<int:pk>/',        views.education_form, name='education_form'),
    path('employee/<int:empl>/education/<int:pk>/delete/', views.education_del,  name='education_del'),
                                                               
    path('employee/<int:empl>/fio_hists/',                 views.fio_hist_list,  name='fio_hist_list'),
    path('employee/<int:empl>/fio_hists/create/',          views.fio_hist_add,   name='fio_hist_add'),
    path('employee/<int:empl>/fio_hist/<int:pk>/',         views.fio_hist_form,  name='fio_hist_form'),
    path('employee/<int:empl>/fio_hist/<int:pk>/delete/',  views.fio_hist_del,   name='fio_hist_del'),
                                         
    path('employee/<int:empl>/children/',                  views.child_list,     name='child_list'),
    path('employee/<int:empl>/childs/create/',             views.child_add,      name='child_add'),
    path('employee/<int:empl>/child/<int:pk>/',            views.child_form,     name='child_form'),
    path('employee/<int:empl>/child/<int:pk>/delete/',     views.child_del,      name='child_del'),
                                         
    path('employee/<int:empl>/period/',                    views.empl_per_form,  name='empl_per_form'),
                                                              
    path('employee/<int:empl>/accruals/',                  views.accrual_list,   name='accrual_list'),
    path('employee/<int:empl>/accruals/create/',           views.accrual_add,    name='accrual_add'),
    path('employee/<int:empl>/accrual/<int:pk>/',          views.accrual_form,   name='accrual_form'),
    path('employee/<int:empl>/accrual/<int:pk>/delete/',   views.accrual_del,    name='accrual_del'),
                                                               
    path('employee/<int:empl>/payouts/',                   views.payout_list,    name='payout_list'),
    path('employee/<int:empl>/payouts/create/',            views.payout_add,     name='payout_add'),
    path('employee/<int:empl>/payout/<int:pk>/',           views.payout_form,    name='payout_form'),
    path('employee/<int:empl>/payout/<int:pk>/delete/',    views.payout_del,     name='payout_del'),
]
