from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.shortcuts import get_object_or_404

from hier.utils import get_base_context
from .forms import WageForm,  PeriodForm,  DepartForm,  DepHistForm,  PostForm,  EmployeeForm,  FioHistForm,  ChildForm,  AppointForm,  EducationForm,  EmplInfoForm, PayTitleForm,  AccrualForm, PayoutForm
from .models import Period, Depart, DepHist, Post, Employee, FioHist, Child, Appoint, Education, EmplPer, PayTitle, Payment, Params
from .wage_xml import delete_all, import_all
from .tree import build_tree




#----------------------------------
# Main
#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def index(request):
    stat = []
    stat.append(['Period',    len(Period.objects.all())])
    stat.append(['Depart',    len(Depart.objects.all())])
    stat.append(['DepHist',   len(DepHist.objects.all())])
    stat.append(['Post',      len(Post.objects.all())])
    stat.append(['Employee',  len(Employee.objects.all())])
    stat.append(['FioHist',   len(FioHist.objects.all())])
    stat.append(['Child',     len(Child.objects.all())])
    stat.append(['Appoint',   len(Appoint.objects.all())])
    stat.append(['Education', len(Education.objects.all())])
    stat.append(['EmplPer',   len(EmplPer.objects.all())])
    stat.append(['PayTitle',  len(PayTitle.objects.all())])
    stat.append(['Payment',   len(Payment.objects.all())])

    param = get_param(request.user)
    context = get_base_context(request, 0, 0, 'Работа', 'content_list')
    context['period_form'] = get_period_form(request, param)
    context['tree'] = build_tree(request.user, 0, param.d_scan())
    context['stat'] = stat
    template = loader.get_template('wage/index.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
# Tree node toggle
#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def tree(request, pk):
    depart = Depart.objects.get(id = pk)
    if (depart != None):
        depart.is_open = not depart.is_open
        depart.save()
    return HttpResponseRedirect(reverse('wage:index'))

#----------------------------------
# Delete all data!
#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def clear(request):
    delete_all()
    return HttpResponseRedirect(reverse('wage:index'))

#----------------------------------
# Import from XML
#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def xml_import(request):
    imp_data  = []
    imp_errors = []
    import_all(request.user, imp_data, imp_errors)
    return HttpResponseRedirect(reverse('wage:index'))

              
#----------------------------------
# Depart
#----------------------------------
def depart_list(request):
    data = Depart.objects.filter(user = request.user.id).order_by('sort')
    return list_view(request, 0, 'Отделы', 'depart', data)

#----------------------------------
def depart_add(request):
    if (request.method == 'POST'):
        form = DepartForm(request.POST)
    else:
        form = DepartForm(initial = {'name': '', 'sort': '',})
    return depart_form_view(request, 0, 'Отдел', 'depart', form)

#----------------------------------
def depart_form(request, pk):
    data = get_object_or_404(Depart.objects.filter(id = pk).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = DepartForm(request.POST, instance = data)
    else:
        form = DepartForm(instance = data)
    return depart_form_view(request, pk, 'Отдел', 'depart', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def depart_del(request, pk):
    Depart.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('wage:depart_list'))

              
#----------------------------------
# DepHist
#----------------------------------
def dep_hist_add(request, dep):
    depart = get_object_or_404(Depart.objects.filter(id = dep, user = request.user.id))
    if (request.method != 'POST'):
        form = DepHistForm(request.user, initial = {'dBeg': datetime.today(), 'node': None,})
    else:
        form = DepHistForm(request.user, request.POST)
    return dep_info_form_view(request, depart, 0, 'Изменение подчиненности отдела', 'dep_hist', form)
              
#----------------------------------
def dep_hist_form(request, dep, pk):
    data = get_object_or_404(DepHist.objects.filter(id = pk, depart = dep))
    depart = get_object_or_404(Depart.objects.filter(id = data.depart.id, user = request.user.id))
    if (request.method == 'POST'):
        form = DepHistForm(request.user, request.POST, instance = data)
    else:
        form = DepHistForm(request.user, instance = data)
    return dep_info_form_view(request, depart, pk, 'Изменение подчиненности отдела', 'dep_hist', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def dep_hist_del(request, dep, pk):
    depart = get_object_or_404(Depart.objects.filter(id = dep, user = request.user.id))
    DepHist.objects.get(id = pk, depart = dep).delete()
    return HttpResponseRedirect(reverse('wage:depart_form', args=(dep,)))


#----------------------------------
# Post
#----------------------------------
def post_list(request):
    data = Post.objects.filter(user = request.user.id).order_by('name')
    return list_view(request, 0, 'Должности', 'post', data)

#----------------------------------
def post_add(request):
    if (request.method == 'POST'):
        form = PostForm(request.POST)
    else:
        form = PostForm(initial = {'name': '',})
    return form_view(request, 0, 0, 'Должность', 'post', form)
              
#----------------------------------
def post_form(request, pk):
    data = get_object_or_404(Post.objects.filter(id = pk).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = PostForm(request.POST, instance = data)
    else:
        form = PostForm(instance = data)
    return form_view(request, 0, pk, 'Должность', 'post', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def post_del(request, pk):
    Post.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('wage:post_list'))


#----------------------------------
# PayTitle
#----------------------------------
def pay_title_list(request):
    data = PayTitle.objects.filter(user = request.user.id).order_by('name')
    return list_view(request, 0, 'Виды начислений и выплат', 'pay_title', data)

#----------------------------------
def pay_title_add(request):
    if (request.method == 'POST'):
        form = PayTitleForm(request.POST)
    else:
        form = PayTitleForm(initial = {'name': '',})
    return form_view(request, 0, 0, 'Наименование начисления или выплаты', 'pay_title', form)

#----------------------------------
def pay_title_form(request, pk):
    data = get_object_or_404(PayTitle.objects.filter(id = pk))
    if (request.method == 'POST'):
        form = PayTitleForm(request.POST, instance = data)
    else:
        form = PayTitleForm(instance = data)
    return form_view(request, 0, pk, 'Наименование начисления или выплаты', 'pay_title', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def pay_title_del(request, pk):
    PayTitle.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('wage:pay_title_list'))


#----------------------------------
# Period
#----------------------------------
def period_list(request):
    data = Period.objects.filter(user = request.user.id).order_by('-dBeg')
    return list_view(request, 0, 'Расчетные периоды', 'period', data)

#----------------------------------
def period_add(request):
    if (request.method == 'POST'):
        form = PeriodForm(request.POST)
    else:
        form = PeriodForm(initial = {'dBeg': datetime(datetime.today().year, datetime.today().month, 1),})
    return form_view(request, 0, 0, 'Расчетный период', 'period', form)

#----------------------------------
def period_form(request, pk):
    data = get_object_or_404(Period.objects.filter(id = pk).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = PeriodForm(request.POST, instance = data)
    else:
        form = PeriodForm(instance = data)
    return form_view(request, 0, pk, 'Расчетный период', 'period', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def period_del(request, pk):
    Period.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('wage:period_list'))


#----------------------------------
# Employee
#----------------------------------
def empl_list(request):
    data = Employee.objects.filter(user = request.user.id).order_by('sort')
    return list_view(request, 0, 'Сотрудники', 'empl', data)

#----------------------------------
def empl_add(request):
    if (request.method == 'POST'):
        form = EmployeeForm(request.POST)
    else:
        form = EmployeeForm()
    return form_view(request, 0, 0, 'Сотрудник', 'empl', form)

#----------------------------------
def empl_form(request, pk):
    data = get_object_or_404(Employee.objects.filter(id = pk).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = EmployeeForm(request.POST, instance = data)
    else:
        form = EmployeeForm(instance = data)
    return form_view(request, 0, pk, 'Сотрудник', 'empl', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def empl_del(request, pk):
    Employee.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('wage:empl_list'))


#----------------------------------
# Appoint
#----------------------------------
def appoint_list(request, empl):
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    data = Appoint.objects.filter(employee = empl).order_by('-dBeg')
    return list_view(request, employee, 'Назначения', 'appoint', data)

#----------------------------------
def appoint_add(request, empl):
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = AppointForm(request.POST)
    else:
        form = AppointForm()
    return form_view(request, employee, 0, 'Назначение', 'appoint', form)

#----------------------------------
def appoint_form(request, empl, pk):
    data = get_object_or_404(Appoint.objects.filter(id = pk))
    employee = get_object_or_404(Employee.objects.filter(id = data.employee.id).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = AppointForm(request.POST, instance = data)
    else:
        form = AppointForm(instance = data)
    return form_view(request, employee, pk, 'Назначение', 'appoint', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def appoint_del(request, empl, pk):
    Appoint.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('wage:appoint_list', args=(empl,)))


#----------------------------------
# Education
#----------------------------------
def education_list(request, empl):
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    data = Education.objects.filter(employee = empl).order_by('-dBeg')
    return list_view(request, employee, 'Образование', 'education', data)

#----------------------------------
def education_add(request, empl):
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = EducationForm(request.POST)
    else:
        form = EducationForm(initial = {'dEnd': datetime.today(),})
    return form_view(request, employee, 0, 'Образование', 'education', form)

#----------------------------------
def education_form(request, empl, pk):
    data = get_object_or_404(Education.objects.filter(id = pk))
    if (request.method == 'POST'):
        form = EducationForm(request.POST, instance = data)
    else:
        form = EducationForm(instance = data)
    return form_view(request, data.employee, pk, 'Образование', 'education', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def education_del(request, empl, pk):
    Education.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('wage:education_list', args=(empl,)))


#----------------------------------
# FioHist
#----------------------------------
def fio_hist_list(request, empl):
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    data = FioHist.objects.filter(employee = empl).order_by('-dEnd')
    return list_view(request, employee, 'Изменения фамилии', 'fio_hist', data)

#----------------------------------
def fio_hist_add(request, empl):
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = FioHistForm(request.POST)
    else:
        form = FioHistForm(initial = {'dEnd': datetime.today(),})
    return form_view(request, employee, 0, 'Изменение фамилии', 'fio_hist', form)

#----------------------------------
def fio_hist_form(request, empl, pk):
    data = get_object_or_404(FioHist.objects.filter(id = pk))
    if (request.method == 'POST'):
        form = FioHistForm(request.POST, instance = data)
    else:
        form = FioHistForm(instance = data)
    return form_view(request, data.employee, pk, 'Изменение фамилии', 'fio_hist', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def fio_hist_del(request, empl, pk):
    FioHist.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('wage:fio_hist_list', args=(empl,)))

              
#----------------------------------
# Child
#----------------------------------
def child_list(request, empl):
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    data = Child.objects.filter(employee = empl).order_by('-born')
    return list_view(request, employee, 'Дети', 'child', data)

#----------------------------------
def child_add(request, empl):
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = ChildForm(request.POST)
    else:
        form = ChildForm(initial = {'born': datetime.today(),})
    return form_view(request, employee, 0, 'Ребёнок', 'child', form)

#----------------------------------
def child_form(request, empl, pk):
    data = get_object_or_404(Child.objects.filter(id = pk))
    if (request.method == 'POST'):
        form = ChildForm(request.POST, instance = data)
    else:
        form = ChildForm(instance = data)
    return form_view(request, data.employee, pk, 'Ребёнок', 'child', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def child_del(request, empl, pk):
    Child.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('wage:child_list', args=(empl,)))

              
#----------------------------------
# Employee Period Info
#----------------------------------
def empl_per_form(request, empl, y, m):
    param = get_param(request.user)
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    empl_per = None
    rate = 1
    if (len(EmplPer.objects.filter(employee = empl, period = param.period)) > 0):
        empl_per = EmplPer.objects.filter(employee = empl, period = param.period)[0]
        rate = empl_per.salaryRate
    accrued = paid_out = debt_in_v = accrued_v = paid_out_v = debt_out_v = salary = 0
    d_beg = d_end = None
    currency = department = post = ''
    appoints = Appoint.objects.filter(employee = empl, dBeg__lte = param.period.dBeg).order_by('-dBeg')
    if (len(appoints) > 0):
        d_beg = appoints[0].dBeg
        d_end = appoints[0].dEnd
        salary = appoints[0].salary
        currency = appoints[0].currency
        department = appoints[0].depart.name
        post = appoints[0].post.name
    form = EmplInfoForm(request.user, instance = empl_per, initial = {'appoint_beg': d_beg,
                                                                      'appoint_end': d_end,
                                                                      'fio': employee.fio,
                                                                      'salary': salary,
                                                                      'currency': currency,
                                                                      'department': department,
                                                                      'post': post,
                                                                      'plan_days': param.period.planDays,
                                                                      'accrued': accrued,
                                                                      'paid_out': paid_out,
                                                                      'debt_in_v': debt_in_v,
                                                                      'accrued_v': accrued_v,
                                                                      'paid_out_v': paid_out_v,
                                                                      'debt_out_v': debt_out_v,
                                                                      })
    return form_view(request, employee, 0, 'Итоги за месяц', 'empl_per', form)

              
#----------------------------------
# Accrual
#----------------------------------
def accrual_list(request, empl, y, m):
    param = get_param(request.user)
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    data = Payment.objects.filter(employee = empl, period = param.period.id, direct = 0).order_by('-payed')
    return list_view(request, employee, 'Начисления', 'accrual', data)

#----------------------------------
def accrual_add(request, empl, y, m):
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = AccrualForm(request.POST)
    else:
        form = AccrualForm()
    return form_view(request, employee, 0, 'Начисление', 'accrual', form)

#----------------------------------
def accrual_form(request, empl, y, m, pk):
    data = get_object_or_404(Payment.objects.filter(id = pk))
    employee = get_object_or_404(Employee.objects.filter(id = data.employee.id).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = AccrualForm(request.POST, instance = data)
    else:
        form = AccrualForm(instance = data)
    return form_view(request, employee, pk, 'Начисление', 'accrual', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def accrual_del(request, empl, y, m, pk):
    Payment.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('wage:accrual_list', args=(empl, y, m,)))


#----------------------------------
# Payout
#----------------------------------
def payout_list(request, empl, y, m):
    param = get_param(request.user)
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    data = Payment.objects.filter(employee = empl, period = param.period.id, direct = 1).order_by('-payed')
    return list_view(request, employee, 'Выплаты', 'payout', data)

#----------------------------------
def payout_add(request, empl, y, m):
    employee = get_object_or_404(Employee.objects.filter(id = empl).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = PayoutForm(request.POST)
    else:
        form = PayoutForm()
    return form_view(request, employee, 0, 'Выплата', 'payout', form)

#----------------------------------
def payout_form(request, empl, y, m, pk):
    data = get_object_or_404(Payment.objects.filter(id = pk))
    employee = get_object_or_404(Employee.objects.filter(id = data.employee.id).filter(user = request.user.id))
    if (request.method == 'POST'):
        form = PayoutForm(request.POST, instance = data)
    else:
        form = PayoutForm(instance = data)
    return form_view(request, employee, pk, 'Выплата', 'payout', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def payout_del(request, empl, y, m, pk):
    Payment.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('wage:payout_list', args=(empl, y, m,)))







def get_param(user):
    if (len(Params.objects.filter(user = user.id)) > 0):
        par = Params.objects.filter(user = user.id)[0]
        if (not par.period):
            if (len(Period.objects.filter(user = user.id)) > 0):
                par.period = Period.objects.filter(user = user.id).order_by('-dBeg')[0]
                par.save()
        return par
    else:
        per = None
        if (len(Period.objects.filter(user = user.id)) > 0):
            per = Period.objects.filter(user = user.id).order_by('-dBeg')[0]
        return Params.objects.create(user = user, period = per)


def get_period_form(request, param):
    if (request.method != 'POST'):
        f = WageForm(instance = param)
        f.fields['period'].queryset = Period.objects.filter(user = request.user.id).order_by('-dBeg')
    else:
        f = WageForm(request.POST, instance = param)
        f.fields['period'].queryset = Period.objects.filter(user = request.user.id).order_by('-dBeg')
        if f.is_valid():
            f.save()
    return f


#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def list_view(request, employee, title, name, data):
    empl = 0
    if employee:
        empl = employee.id
    param = get_param(request.user)
    context = get_base_context(request, 0, 0, title, 'content_list')
    context['period_form'] = get_period_form(request, param)
    context['tree'] = build_tree(request.user, 0, param.d_scan())
    context[name + 's'] = data
    context['employee'] = employee
    context['y'] = param.period.dBeg.year
    context['m'] = param.period.dBeg.month
    template = loader.get_template('wage/' + name + '_list.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def form_view(request, employee, pk, title, name, form):
    empl = 0
    if employee:
        empl = employee.id
    
    param = get_param(request.user)
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            if employee:
                data.employee = employee
            else:
                data.user = request.user
            if (name == 'accrual') or (name == 'payout'):
                data.period = param.period
                if (name == 'accrual'):
                    data.direct = 0
                else:
                    data.direct = 1
            form.save()
            if (name == 'accrual') or (name == 'payout'):
                return HttpResponseRedirect(reverse('wage:' + name + '_list', args=(empl, param.period.dBeg.year, param.period.dBeg.month,)))
            elif empl:
                return HttpResponseRedirect(reverse('wage:' + name + '_list', args=(empl,)))
            else:
                return HttpResponseRedirect(reverse('wage:' + name + '_list'))

    if (name == 'appoint'):
        form.fields['depart'].queryset = Depart.objects.filter(user = request.user.id).order_by('name')
        form.fields['post'].queryset   = Post.objects.filter(user = request.user.id).order_by('name')
    
    if (name == 'accrual') or (name == 'payout'):
        form.fields['title'].queryset = PayTitle.objects.filter(user = request.user.id).order_by('name')
    
    context = get_base_context(request, 0, pk, title)
    context['period_form'] = None
    context['current_period'] = param.period
    context['tree'] = build_tree(request.user, 0, param.d_scan())
    context['form'] = form
    context['employee'] = employee
    context['y'] = param.period.dBeg.year
    context['m'] = param.period.dBeg.month
    template = loader.get_template('wage/' + name + '_form.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def depart_list_view(request, dep, pk, title, name, data):
    param = get_param(request.user)
    context = get_base_context(request, 0, pk, title, 'content_list')
    context['period_form'] = get_period_form(request, param)
    context['tree'] = build_tree(request.user, 0, param.d_scan())
    context[name + 's'] = data
    context['dep'] = dep
    template = loader.get_template('wage/' + name + '_list.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
# Depart Form (дополнительная панель - история DepHist)
#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def depart_form_view(request, pk, title, name, form):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.user = request.user
            form.save()
            return HttpResponseRedirect(reverse('wage:depart_list'))
    param = get_param(request.user)
    context = get_base_context(request, 0, pk, 'Отдел')
    context['period_form'] = None
    context['current_period'] = param.period
    context['tree'] = build_tree(request.user, 0, param.d_scan())
    context['form'] = form
    context['empl_id'] = 0
    context['dep_hists'] = DepHist.objects.filter(user = request.user.id, depart = pk).order_by('-dBeg')
    template = loader.get_template('wage/depart_form.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
# Depart Subitem Form (DepHist)
#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
#----------------------------------
def dep_info_form_view(request, depart, pk, title, name, form):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.user = request.user
            data.depart = depart
            form.save()
            return HttpResponseRedirect(reverse('wage:depart_form', args=(depart.id,)))
    
    param = get_param(request.user)
    context = get_base_context(request, 0, pk, title)
    context['period_form'] = None
    context['current_period'] = param.period
    context['tree'] = build_tree(request.user, 0, param.d_scan())
    context['form'] = form
    context['depart'] = depart
    template = loader.get_template('wage/' + name + '_form.html')
    return HttpResponse(template.render(context, request))



