import os, locale
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q

from hier.utils import get_base_context_ext, process_common_commands, extract_get_params
from hier.params import get_search_info, set_restriction, set_article_kind, set_article_visible, get_search_mode
from hier.models import get_app_params, toggle_content_group
from hier.aside import Fix
from hier.content import find_group
from .models import app_name, set_active, Period, Depart, DepHist, Post, Employee, FioHist, Child, Appoint, Education, EmplPer, PayTitle, Payment
from .forms import PeriodForm, DepartForm, DepHistForm, PostForm, EmployeeForm, FioHistForm, ChildForm, AppointForm, EducationForm, EmplPerForm, PayTitleForm, PaymentForm

items_per_page = 50

# Представления
PER = 'period'
POST = 'post'
TITLE = 'pay_title'
DEP_LIST = 'department' # Список подразделений
DEP_HIST = 'dep_hist' # Список изменений подразделения
DEP_INFO = 'dep_info' # Форма подразделения
EMPL_LIST = 'employee' # Список сотрудников
EMPL_INFO = 'total' # Форма сотрудника
ACC = 'accrual'
PAY = 'payment'
APP = 'appoint'
EDUC = 'education'
CHLD = 'child'
SUR = 'surname'
REPORT = 'report'

# Фразы "Добавить <сущность>"
ADD_ENTITY = {
    EMPL_LIST: _('add employee'),
    DEP_LIST: _('add department'),
    POST: _('add post'),
    TITLE: _('add pay title'),
    EDUC: _('add education'),
    SUR: _('add surname'),
    CHLD: _('add child'),
    }

ALL_RESTRICTIONS = (PER, POST, TITLE, DEP_LIST, DEP_HIST, DEP_INFO, EMPL_LIST, EMPL_INFO, ACC, PAY, APP, EDUC, CHLD, SUR, REPORT) # Все возможные представления
EMPL_ASIDE = (EMPL_INFO, ACC, PAY, APP, EDUC, CHLD, SUR) # Это сущности для конкретного сотрудника
HIDE_ITEM_INPUT = (PER, DEP_HIST, EMPL_INFO, ACC, PAY, APP) # Это сущности, при создании которых не надо предварительно указывать наименование
SHOW_SELECTOR = (PER) # Сущности, для которых в списке слева надо показывать селектор

# Захардкодженный производственный календарь
# http://www.calendar.by/?year=2021
PROD_CAL = { '2020.10': 22, '2020.11': 21, '2020.12': 22,
             '2021.01': 19, '2021.02': 20, '2021.03': 22,
             '2021.04': 22, '2021.05': 21, '2021.06': 22,
             '2021.07': 22, '2021.08': 22, '2021.09': 22,
             '2021.10': 21, '2021.11': 22, '2021.12': 23, }

#----------------------------------
def set_restriction_and_redirect(request, restriction, save_context = False):
    add = ''
    if save_context:
        add = extract_get_params(request)
    set_restriction(request.user, app_name, restriction)
    return HttpResponseRedirect(reverse('wage:main') + add)

def periods(request):
    return set_restriction_and_redirect(request, PER)

def posts(request):
    return set_restriction_and_redirect(request, POST)

def pay_titles(request):
    return set_restriction_and_redirect(request, TITLE)

def departments(request):
    return set_restriction_and_redirect(request, DEP_LIST)

def dep_hist(request):
    return set_restriction_and_redirect(request, DEP_HIST)

def dep_info(request):
    return set_restriction_and_redirect(request, DEP_INFO)

def employees(request):
    return set_restriction_and_redirect(request, EMPL_LIST)

def total(request):
    return set_restriction_and_redirect(request, EMPL_INFO)

def accrual(request):
    return set_restriction_and_redirect(request, ACC)

def payment(request):
    return set_restriction_and_redirect(request, PAY)

def appoint(request):
    return set_restriction_and_redirect(request, APP)

def education(request):
    return set_restriction_and_redirect(request, EDUC)

def child(request):
    return set_restriction_and_redirect(request, CHLD)

def surname(request):
    return set_restriction_and_redirect(request, SUR)

def reports(request):
    return set_restriction_and_redirect(request, REPORT)

def toggle(request, pk):
    toggle_content_group(request.user.id, app_name, pk)
    return HttpResponseRedirect(reverse('wage:main') + extract_get_params(request))

def item_form(request, pk):
    app_param = get_app_params(request.user, app_name)
    if (app_param.restriction == EMPL_LIST):
        set_restriction(request.user, app_name, EMPL_INFO)
        item = Employee.objects.filter(id = pk).get()
        item.set_active()
        set_article_kind(request.user, app_name, '', item.id)
    elif (app_param.restriction == DEP_LIST):
        set_restriction(request.user, app_name, DEP_HIST)
        item = Depart.objects.filter(id = pk).get()
        item.set_active()
        set_article_kind(request.user, app_name, '', item.id)
    elif (app_param.restriction == DEP_INFO):
        set_restriction(request.user, app_name, DEP_HIST)
        set_article_kind(request.user, app_name, '', pk)
    else:
        set_article_kind(request.user, app_name, '', pk)
    return HttpResponseRedirect(reverse('wage:main') + extract_get_params(request))

def item2_form(request, pk):
    app_param = get_app_params(request.user, app_name)
    if (app_param.restriction == EMPL_INFO):
        set_article_kind(request.user, app_name, '', pk)
    if (app_param.restriction == DEP_HIST):
        set_article_kind(request.user, app_name, '', pk)
        set_restriction(request.user, app_name, DEP_INFO)
    return HttpResponseRedirect(reverse('wage:main') + extract_get_params(request))

#----------------------------------
# Index
#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def main(request):
    app_param = get_app_params(request.user, app_name)
    if (app_param.restriction not in ALL_RESTRICTIONS):
        return set_restriction_and_redirect(request, PER)

    if not Period.objects.filter(user = request.user.id, active = True).exists():
        if (app_param.restriction != PER):
            return set_restriction_and_redirect(request, PER)

    period = None
    if Period.objects.filter(user = request.user.id, active = True).exists():
        period = Period.objects.filter(user = request.user.id, active = True).get()
    
    if (app_param.restriction in EMPL_ASIDE):
        if not Employee.objects.filter(user = request.user.id, active = True).exists():
            return set_restriction_and_redirect(request, EMPL_LIST)

    employee = None
    if Employee.objects.filter(user = request.user.id, active = True).exists():
        employee = Employee.objects.filter(user = request.user.id, active = True).get()

    if (app_param.restriction == DEP_HIST):
        if not Depart.objects.filter(user = request.user.id, active = True).exists():
            return set_restriction_and_redirect(request, DEP_LIST)

    depart = None
    if Depart.objects.filter(user = request.user.id, active = True).exists():
        depart = Depart.objects.filter(user = request.user.id, active = True).get()

    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('wage:main') + extract_get_params(request))

    # для трансляции строкового представления дат, в частности в item_info
    locale.setlocale(locale.LC_CTYPE, request.LANGUAGE_CODE)
    locale.setlocale(locale.LC_TIME, request.LANGUAGE_CODE)

    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item-add' in request.POST):
            if (app_param.restriction == PER):
                item_id = add_period(request)
            if (app_param.restriction == POST):
                item_id = add_post(request)
            if (app_param.restriction == TITLE):
                item_id = add_pay_title(request)
            if (app_param.restriction == DEP_LIST):
                item_id = add_department(request)
            if (app_param.restriction in (DEP_HIST, DEP_INFO)):
                item_id = add_dep_hist(request, depart)
            if (app_param.restriction == EMPL_LIST):
                item_id = add_employee(request)
            if (app_param.restriction == ACC):
                item_id = add_payment(request, period, employee, 0)
            if (app_param.restriction == PAY):
                item_id = add_payment(request, period, employee, 1)
            if (app_param.restriction == APP):
                item_id = add_appoint(request, period, employee)
            if (app_param.restriction == EDUC):
                item_id = add_education(request, period, employee)
            if (app_param.restriction == CHLD):
                item_id = add_child(request, period, employee)
            if (app_param.restriction == SUR):
                item_id = add_surname(request, period, employee)
            return HttpResponseRedirect(reverse('wage:item_form', args = [item_id]))
        if ('item-in-list-select' in request.POST) and (app_param.restriction == PER):
            pk = request.POST['item-in-list-select']
            if pk:
                set_active(request.user.id, pk)
                return HttpResponseRedirect(reverse('wage:item_form', args = [pk]) + extract_get_params(request))

    app_param, context = get_base_context_ext(request, app_name, 'main', get_title(app_param.restriction, employee, depart))

    redirect = False

    if app_param.article:
        valid_article = False
        if (app_param.restriction == PER):
            valid_article = Period.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if (app_param.restriction == POST):
            valid_article = Post.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if (app_param.restriction == TITLE):
            valid_article = PayTitle.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if (app_param.restriction == DEP_HIST):
            valid_article = DepHist.objects.filter(id = app_param.art_id, depart = depart.id).exists()
        if (app_param.restriction == DEP_INFO):
            valid_article = Depart.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if (app_param.restriction == EMPL_INFO):
            valid_article = Employee.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if (app_param.restriction == ACC):
            valid_article = Payment.objects.filter(id = app_param.art_id, employee = employee.id, period = period.id, direct = 0).exists()
        if (app_param.restriction == PAY):
            valid_article = Payment.objects.filter(id = app_param.art_id, employee = employee.id, period = period.id, direct = 1).exists()
        if (app_param.restriction == APP):
            valid_article = Appoint.objects.filter(id = app_param.art_id, employee = employee.id).exists()
        if (app_param.restriction == EDUC):
            valid_article = Education.objects.filter(id = app_param.art_id, employee = employee.id).exists()
        if (app_param.restriction == CHLD):
            valid_article = Child.objects.filter(id = app_param.art_id, employee = employee.id).exists()
        if (app_param.restriction == SUR):
            valid_article = FioHist.objects.filter(id = app_param.art_id, employee = employee.id).exists()
        if (app_param.restriction == REPORT):
            valid_article = True

        if valid_article:
            if (app_param.restriction == PER):
                item = get_object_or_404(Period.objects.filter(id = app_param.art_id, user = request.user.id))
                disable_delete = item.active or EmplPer.objects.filter(period = item.id).exists() or \
                                                Payment.objects.filter(period = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, disable_delete)
            if (app_param.restriction == POST):
                item = get_object_or_404(Post.objects.filter(id = app_param.art_id, user = request.user.id))
                disable_delete = Appoint.objects.filter(post = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, disable_delete)
            if (app_param.restriction == TITLE):
                item = get_object_or_404(PayTitle.objects.filter(id = app_param.art_id, user = request.user.id))
                disable_delete = Payment.objects.filter(title = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, disable_delete)
            if (app_param.restriction == DEP_HIST):
                item = get_object_or_404(DepHist.objects.filter(id = app_param.art_id, depart = depart.id))
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, False)
            if (app_param.restriction == DEP_INFO):
                item = get_object_or_404(Depart.objects.filter(id = app_param.art_id, user = request.user.id))
                disable_delete = DepHist.objects.filter(depart = item.id).exists() or \
                                 DepHist.objects.filter(node = item.id).exists() or \
                                 Appoint.objects.filter(depart = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, disable_delete)
            if (app_param.restriction == EMPL_INFO):
                item = get_object_or_404(Employee.objects.filter(id = app_param.art_id, user = request.user.id))
                disable_delete = FioHist.objects.filter(employee = item.id).exists() or \
                                 Child.objects.filter(employee = item.id).exists() or \
                                 Appoint.objects.filter(employee = item.id).exists() or \
                                 Education.objects.filter(employee = item.id).exists() or \
                                 Payment.objects.filter(employee = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, disable_delete)
            if (app_param.restriction == ACC):
                item = get_object_or_404(Payment.objects.filter(id = app_param.art_id, employee = employee.id, period = period.id, direct = 0))
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, False)
            if (app_param.restriction == PAY):
                item = get_object_or_404(Payment.objects.filter(id = app_param.art_id, employee = employee.id, period = period.id, direct = 1))
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, False)
            if (app_param.restriction == APP):
                item = get_object_or_404(Appoint.objects.filter(id = app_param.art_id, employee = employee.id))
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, False)
            if (app_param.restriction == EDUC):
                item = get_object_or_404(Education.objects.filter(id = app_param.art_id, employee = employee.id))
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, False)
            if (app_param.restriction == CHLD):
                item = get_object_or_404(Child.objects.filter(id = app_param.art_id, employee = employee.id))
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, False)
            if (app_param.restriction == SUR):
                item = get_object_or_404(FioHist.objects.filter(id = app_param.art_id, employee = employee.id))
                redirect = edit_item(request, context, app_param.restriction, period, employee, depart, item, False)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
    if (request.method == 'POST'):
        if ('total-save' in request.POST):
            total_save(request, context, period, employee)
    else:
        check_empl_per(request.user, context, app_param, period, employee)

    if redirect:
        return HttpResponseRedirect(reverse('wage:main') + extract_get_params(request))

    fixes = []
    if (app_param.restriction in EMPL_ASIDE):
        fixes.append(Fix(PER, _('periods').capitalize(), 'todo/icon/planned.png', 'periods/', len(Period.objects.filter(user = request.user.id))))
        fixes.append(Fix(EMPL_LIST, _('employees').capitalize(), 'rok/icon/user.png', 'employees/', len(Employee.objects.filter(user = request.user.id))))
        fixes.append(Fix(EMPL_INFO, _('totals').capitalize(), 'todo/icon/myday.png', 'total/', None))
        fixes.append(Fix(ACC, _('accruals').capitalize(), 'todo/icon/myday.png', 'accrual/', len(Payment.objects.filter(employee = employee.id, period = period.id, direct = 0))))
        fixes.append(Fix(PAY, _('pays').capitalize(), 'todo/icon/myday.png', 'payment/', len(Payment.objects.filter(employee = employee.id, period = period.id, direct = 1))))
        fixes.append(Fix(APP, _('appointments').capitalize(), 'todo/icon/myday.png', 'appoint/', len(Appoint.objects.filter(employee = employee.id))))
        fixes.append(Fix(EDUC, _('educations').capitalize(), 'todo/icon/myday.png', 'education/', len(Education.objects.filter(employee = employee.id))))
        fixes.append(Fix(SUR, _('surnames').capitalize(), 'todo/icon/myday.png', 'surname/', len(FioHist.objects.filter(employee = employee.id))))
        fixes.append(Fix(CHLD, _('children').capitalize(), 'todo/icon/myday.png', 'child/', len(Child.objects.filter(employee = employee.id))))
    elif (app_param.restriction in (DEP_HIST, DEP_INFO)):
        fixes.append(Fix(DEP_LIST, _('departments').capitalize(), 'rok/icon/home.png', 'departments/', len(Depart.objects.filter(user = request.user.id))))
        fixes.append(Fix(DEP_HIST, _('department history').capitalize(), 'rok/icon/home.png', 'dep_hist/', len(DepHist.objects.filter(depart = depart.id))))
    else:
        fixes.append(Fix(PER, _('periods').capitalize(), 'todo/icon/planned.png', 'periods/', len(Period.objects.filter(user = request.user.id))))
        fixes.append(Fix(EMPL_LIST, _('employees').capitalize(), 'rok/icon/user.png', 'employees/', len(Employee.objects.filter(user = request.user.id))))
        fixes.append(Fix(DEP_LIST, _('departments').capitalize(), 'rok/icon/home.png', 'departments/', len(Depart.objects.filter(user = request.user.id))))
        fixes.append(Fix(POST, _('posts').capitalize(), 'rok/icon/work.png', 'posts/', len(Post.objects.filter(user = request.user.id))))
        fixes.append(Fix(TITLE, _('pay titles').capitalize(), 'rok/icon/edit.png', 'pay_titles/', len(PayTitle.objects.filter(user = request.user.id))))
        fixes.append(Fix(REPORT, _('reports').capitalize(), 'rok/icon/news.png', 'reports/', 1))

    context['fix_list'] = fixes
    context['without_lists'] = True
    context['hide_important'] = True
    if period:
        context['title_info'] = period.name()

    if (app_param.restriction in HIDE_ITEM_INPUT):
        context['hide_add_item_input'] = True
    if (app_param.restriction not in SHOW_SELECTOR):
        context['hide_selector'] = True
    if (app_param.restriction in ADD_ENTITY):
        context['add_item_placeholder'] = ADD_ENTITY[app_param.restriction].capitalize()
    if (app_param.restriction == EMPL_INFO):
        context['list_id'] = employee.id
    if (app_param.restriction == DEP_HIST):
        context['list_id'] = depart.id

    query = None
    page_number = 1
    if (request.method == 'GET'):
        query = request.GET.get('q')
        page_number = request.GET.get('page')
    context['search_info'] = get_search_info(query)
    data = filtered_sorted_list(request.user, app_param, period, employee, depart, query)

    if (app_param.restriction == EMPL_LIST):
        context['ed_item'] = employee

    if (app_param.restriction == EMPL_LIST):
        groups = []
        for item in data:
            grp_id, grp_name = get_grp_name(item, period.dBeg)
            group = find_group(groups, request.user, app_name, grp_id, grp_name)
            group.items.append(item)
        context['item_groups'] = sorted(groups, key = lambda group: group.grp.grp_id)
        context['page_obj'] = data

    
    paginator = Paginator(data, items_per_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)
    template = loader.get_template('wage/' + app_param.restriction + '.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
def get_title(restriction, employee, depart):
    if (restriction == PER):
        return _('periods').capitalize()
    if (restriction == POST):
        return _('posts').capitalize()
    if (restriction == TITLE):
        return _('pay titles').capitalize()
    if (restriction == DEP_LIST):
        return _('departments').capitalize()
    if (restriction in (DEP_HIST, DEP_INFO)):
        return _('department history').capitalize() + ' ' + depart.name
    if (restriction == EMPL_LIST):
        return _('employees').capitalize()
    if (restriction == EMPL_INFO):
        return employee.fio
    if (restriction == ACC):
        return _('accruals of the employee').capitalize() + ' ' + employee.fio
    if (restriction == PAY):
        return _('payments to the employee').capitalize() + ' ' + employee.fio
    if (restriction == APP):
        return _('appointments of the employee').capitalize() + ' ' + employee.fio
    if (restriction == EDUC):
        return _('educations of the employee').capitalize() + ' ' + employee.fio
    if (restriction == CHLD):
        return _('children of employee').capitalize() + ' ' + employee.fio
    if (restriction == SUR):
        return _('change of surname of employee').capitalize() + ' ' + employee.fio
    if (restriction == REPORT):
        return _('reports').capitalize()
    return 'unknown restriction: ' + str(restriction)

#----------------------------------
def filtered_list(user, restriction, period, employee, depart, query = None):
    if (restriction == PER):
        data = Period.objects.filter(user = user.id)
    elif (restriction == POST):
        data = Post.objects.filter(user = user.id)
    elif (restriction == TITLE):
        data = PayTitle.objects.filter(user = user.id)
    elif (restriction == DEP_LIST):
        data = Depart.objects.filter(user = user.id)
    elif (restriction in (DEP_HIST, DEP_INFO)):
        data = DepHist.objects.filter(depart = depart.id)
    elif (restriction == EMPL_LIST):
        data = Employee.objects.filter(user = user.id)
    elif (restriction == ACC):
        data = Payment.objects.filter(employee = employee.id, period = period.id, direct = 0)
    elif (restriction == PAY):
        data = Payment.objects.filter(employee = employee.id, period = period.id, direct = 1)
    elif (restriction == APP):
        data = Appoint.objects.filter(employee = employee.id)
    elif (restriction == EDUC):
        data = Education.objects.filter(employee = employee.id)
    elif (restriction == CHLD):
        data = Child.objects.filter(employee = employee.id)
    elif (restriction == SUR):
        data = FioHist.objects.filter(employee = employee.id)
    elif (restriction == REPORT):
        data = get_report_data(user, period)
    else:
        data = []

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode != 1):
        return data

    if (restriction == PER):
        lookups = Q(dBeg__icontains = query)
    elif (restriction == POST) or (restriction == TITLE):
        lookups = Q(name__icontains = query)
    elif (restriction == DEP_LIST):
        lookups = Q(name__icontains = query) | Q(sort__icontains = query)
    elif (restriction == EMPL_LIST):
        lookups = Q(fio__icontains = query) | Q(sort__icontains = query) | Q(email__icontains = query) | Q(passw__icontains = query) | \
                  Q(phone__icontains = query) | Q(addr__icontains = query) | Q(info__icontains = query)
    elif (restriction == ACC) or (restriction == PAY):
        lookups = Q(sort__icontains = query) | Q(info__icontains = query)
    elif (restriction == EDUC):
        lookups = Q(institution__icontains = query) | Q(course__icontains = query) | Q(specialty__icontains = query) | Q(qualification__icontains = query) | \
                  Q(document__icontains = query) | Q(number__icontains = query) | Q(city__icontains = query) | Q(info__icontains = query)
    elif (restriction == CHLD):
        lookups = Q(name__icontains = query) | Q(info__icontains = query)
    elif (restriction == SUR):
        lookups = Q(fio__icontains = query) | Q(info__icontains = query)
    else:
        return data

    return data.filter(lookups).distinct()

def filtered_sorted_list(user, app_param, period, employee, depart, query):
    data = filtered_list(user, app_param.restriction, period, employee, depart, query)
    if (app_param.restriction in (PER, DEP_HIST, DEP_INFO, APP)):
        data = data.order_by('-dBeg')
    elif (app_param.restriction in (POST, TITLE, DEP_LIST)):
        data = data.order_by('name')
    elif (app_param.restriction == EMPL_LIST):
        data = data.order_by('fio')
    elif (app_param.restriction in (ACC, PAY)):
        data = data.order_by('-payed')
    elif (app_param.restriction in (EDUC, SUR)):
        data = data.order_by('-dEnd')
    elif (app_param.restriction == CHLD):
        data = data.order_by('-born', 'sort')
    return data


#----------------------------------
def get_grp_name(item, on_date):
    if item.fired(on_date):
        return 99999, _('dismissed').capitalize()
    if Appoint.objects.filter(employee = item.id, dBeg__lte = on_date).exists():
        appoint = Appoint.objects.filter(employee = item.id, dBeg__lte = on_date).order_by('-dBeg')[0]
        if appoint.depart:
            return appoint.depart.id, appoint.depart.name
    return 0, ''


#----------------------------------
def edit_item(request, context, restriction, period, employee, depart, item, disable_delete = False):
    form = None
    if (request.method == 'POST'):
        if ('item_delete' in request.POST):
            delete_item(request, restriction, item, disable_delete)
            return True
        if ('item-in-list-select' in request.POST):
            set_active(request.user.id, item.id)
            return True
        if ('item_save' in request.POST):
            if (restriction == PER):
                form = PeriodForm(request.POST, instance = item)
            elif (restriction == POST):
                form = PostForm(request.POST, instance = item)
            elif (restriction == TITLE):
                form = PayTitleForm(request.POST, instance = item)
            elif (restriction == DEP_HIST):
                form = DepHistForm(request.user, request.POST, instance = item)
            elif (restriction == DEP_INFO):
                form = DepartForm(request.POST, instance = item)
            elif (restriction == EMPL_INFO):
                form = EmployeeForm(request.POST, instance = item)
            elif (restriction in (ACC, PAY)):
                form = PaymentForm(request.POST, instance = item)
            elif (restriction == APP):
                form = AppointForm(request.POST, instance = item)
            elif (restriction == EDUC):
                form = EducationForm(request.POST, instance = item)
            elif (restriction == CHLD):
                form = ChildForm(request.POST, instance = item)
            elif (restriction == SUR):
                form = FioHistForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                if (restriction in EMPL_ASIDE):
                    data.employee = employee
                if (restriction in (DEP_HIST)):
                    data.depart = depart
                form.save()
                return True

    if not form:
        if (restriction == PER):
            form = PeriodForm(instance = item)
            context['item_active'] = item.active
        elif (restriction == POST):
            form = PostForm(instance = item)
        elif (restriction == TITLE):
            form = PayTitleForm(instance = item)
        elif (restriction == DEP_HIST):
            form = DepHistForm(request.user, instance = item)
        elif (restriction == DEP_INFO):
            form = DepartForm(instance = item)
        elif (restriction == EMPL_INFO):
            form = EmployeeForm(instance = item)
        elif (restriction in (ACC, PAY)):
            form = PaymentForm(instance = item)
        elif (restriction == APP):
            form = AppointForm(instance = item)
        elif (restriction == EDUC):
            form = EducationForm(instance = item)
        elif (restriction == CHLD):
            form = ChildForm(instance = item)
        elif (restriction == SUR):
            form = FioHistForm(instance = item)

    context['form'] = form
    context['ed_item'] = item
    return False

#----------------------------------
def delete_item(request, restriction, item, disable_delete = False):
    if disable_delete:
        return False
    if (restriction == EMPL_INFO):
        EmplPer.objects.filter(employee = item.id).delete()
    item.delete()
    set_article_visible(request.user, app_name, False)
    return True

#----------------------------------
def add_period(request):
    y = datetime.today().year
    m = datetime.today().month
    if Period.objects.filter(user = request.user).exists():
        last = Period.objects.filter(user = request.user).order_by('-dBeg')[:1][0]
        y = last.dBeg.year
        m = last.dBeg.month
        if (m < 12):
            m += 1
        else:
            y += 1
            m = 1
    d1 = datetime(y, m, 1).date()
    ppp = '{}.{}'.format(y, str(m).zfill(2))
    pd = 22
    if ppp in PROD_CAL:
        pd = PROD_CAL[ppp]
    d2 = datetime(y, m, 25).date()
    if (d2.weekday() > 4):
        d2 -= timedelta(d2.weekday() - 4)
    if (m < 12):
        m += 1
    else:
        y += 1
        m = 1
    d3 = datetime(y, m, 10).date()
    if (d3.weekday() > 4):
        d3 -= timedelta(d3.weekday() - 4)
    item = Period.objects.create(user = request.user, dBeg = d1, AvansDate = d2, AvansRate = 0, PaymentDate = d3, PaymentRate = 0, planDays = pd)
    return item.id

def add_post(request):
    item = Post.objects.create(user = request.user, name = request.POST['item_add-name'])
    return item.id

def add_pay_title(request):
    item = PayTitle.objects.create(user = request.user, name = request.POST['item_add-name'])
    return item.id

def add_department(request):
    item = Depart.objects.create(user = request.user, name = request.POST['item_add-name'])
    return item.id

def add_dep_hist(request, depart):
    item = DepHist.objects.create(depart = depart)
    set_article_kind(request.user, app_name, '', item.id)
    return item.id

def add_employee(request):
    item = Employee.objects.create(user = request.user, fio = request.POST['item_add-name'])
    set_article_kind(request.user, app_name, '', item.id)
    return item.id

def add_payment(request, period, employee, direct):
    item = Payment.objects.create(period = period, employee = employee, direct = direct, payed = datetime.today(), rate = 0)
    return item.id

def add_appoint(request, period, employee):
    beg = datetime.today().date()
    appoints = Appoint.objects.filter(employee = employee.id).order_by('-dBeg')
    if not appoints:
        item = Appoint.objects.create(employee = employee, dBeg = beg)
    else:
        end = appoints[0].dEnd
        if not appoints[0].dEnd:
            appoints[0].dEnd = beg - timedelta(1)
            appoints[0].save()
        if end and (end < beg):
            end = None
        item = Appoint.objects.create(employee = employee,
                                      tabnum = appoints[0].tabnum,
                                      dBeg = beg,
                                      dEnd = end,
                                      salary = appoints[0].salary,
                                      currency = appoints[0].currency,
                                      depart = appoints[0].depart,
                                      post = appoints[0].post,
                                      taxded = appoints[0].taxded)
    return item.id

def add_education(request, period, employee):
    item = Education.objects.create(employee = employee, institution = request.POST['item_add-name'])
    return item.id

def add_child(request, period, employee):
    item = Child.objects.create(employee = employee, name = request.POST['item_add-name'])
    return item.id

def add_surname(request, period, employee):
    item = FioHist.objects.create(employee = employee, fio = request.POST['item_add-name'])
    return item.id

#----------------------------------
def check_empl_per(user, context, app_param, period, employee):
    if (app_param.restriction != EMPL_INFO):
        return
    debt_in = 0
    priv = 0
    prev_per = period.prev()
    if prev_per:
        if EmplPer.objects.filter(period = prev_per.id, employee = employee.id).exists():
            prev_empl_per = EmplPer.objects.filter(period = prev_per.id, employee = employee.id).get()
            debt_in = prev_empl_per.debtOut
            priv = prev_empl_per.privilege
    if not EmplPer.objects.filter(period = period.id, employee = employee.id).exists():
        empl_per = EmplPer.objects.create(period = period, employee = employee, factDays = period.planDays, debtIn = debt_in, salaryRate = period.PaymentRate, privilege = priv)
    else:
        empl_per = EmplPer.objects.filter(period = period.id, employee = employee.id).get()
    accrued = paid_out = debt_in_v = accrued_v = paid_out_v = debt_out_v = salary = 0
    d_beg = d_end = None
    currency = department = post = ''
    appoints = Appoint.objects.filter(employee = employee.id, dBeg__lte = period.dBeg).order_by('-dBeg')
    if (len(appoints) > 0):
        d_beg = appoints[0].dBeg
        d_end = appoints[0].dEnd
        salary = appoints[0].salary
        currency = appoints[0].currency
        department = appoints[0].depart.name
        if appoints[0].post:
            post = appoints[0].post.name
    context['ep_form'] = EmplPerForm(instance = empl_per)
    context['appoint_end'] = d_end
    context['salary'] = salary
    context['currency'] = currency
    context['department'] = department
    context['post'] = post
    context['plan_days'] = period.planDays
    context['accrued'] = accrued
    context['paid_out'] = paid_out
    context['debt_in_v'] = debt_in_v
    context['accrued_v'] = accrued_v
    context['paid_out_v'] = paid_out_v
    context['debt_out_v'] = debt_out_v

def total_save(request, context, period, employee):
    empl_per = EmplPer.objects.filter(period = period.id, employee = employee.id).get()
    form = EmplPerForm(request.POST, instance = empl_per)
    if form.is_valid():
        data = form.save(commit = False)
        data.period = period
        data.employee = employee
        form.save()
    context['ep_form'] = form

def get_report_data(user, period):
    data = []    
    for employee in Employee.objects.filter(user = user.id):
        #if not EmplPer.objects.filter(period = period.id, employee = employee.id).exists():
        empl_date = None
        contract_date = None
        prev_date = None
        prev_post = None
        prev_salary = 0
        post = None
        salary = 0
        rates = 1
        appoints = Appoint.objects.filter(employee = employee.id, dBeg__lte = period.dBeg).order_by('-dBeg')
        if (len(appoints) > 0):
            appoint = appoints[0]
            if appoint.salary:
                salary = appoint.salary
            contract_date = appoint.dEnd
            if appoint.post:
                post = appoint.post.name
        if (len(appoints) > 1):
            appoint = appoints[1]
            prev_date = appoint.dBeg
            if appoint.post:
                prev_post = appoint.post.name
            prev_salary = appoint.salary
        empl_date = None
        appoints = Appoint.objects.filter(employee = employee.id).order_by('dBeg')
        if (len(appoints) > 0):
            appoint = appoints[0]
            if appoint.dBeg:
                empl_date = appoint.dBeg
        data.append({'employee': employee.fio,
                     'empl_date': empl_date,
                     'contract_date': contract_date,
                     'prev_date': prev_date,
                     'prev_post': prev_post,
                     'prev_salary': prev_salary,
                     'post': post,
                     'salary': salary,
                     'rates': rates,
                     })
    return data
