from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.views import generic
from django.views.generic.edit import UpdateView
from .forms import WageForm, DepartForm, EmployeeForm
from .models import Period, Depart, DepHist, Post, Employee, FioHist, Child, Appoint, Education, EmplPer, PayTitle, Payment, Params
from .wage_xml import delete_all, import_all
from .tree import BuildTree

def get_base_context(request):
    return { 'site_header': get_current_site(request).name, }

def get_stat():
    qty = []
    qty.append(len(Period.objects.all()))
    qty.append(len(Depart.objects.all()))
    qty.append(len(DepHist.objects.all()))
    qty.append(len(Post.objects.all()))
    qty.append(len(Employee.objects.all()))
    qty.append(len(FioHist.objects.all()))
    qty.append(len(Child.objects.all()))
    qty.append(len(Appoint.objects.all()))
    qty.append(len(Education.objects.all()))
    qty.append(len(EmplPer.objects.all()))
    qty.append(len(PayTitle.objects.all()))
    qty.append(len(Payment.objects.all()))
    return qty

def get_param(user_id):
    if (len(Params.objects.filter(user = user_id)) > 0):
        return Params.objects.filter(user = user_id)[0]
    else:
        per = None
        if (len(Period.objects.filter(user = user_id.id)) > 0):
            per = Period.objects.filter(user = user_id.id).order_by('-dBeg')[0]
        return Params.objects.create(user = user_id, period = per)


#----------------------------------
#              INDEX
#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
def index(request):
    param = get_param(request.user)

    if (request.method != 'POST'):
        f = WageForm(instance = param)
        f.fields['period'].queryset = Period.objects.filter(user = request.user.id).order_by('-dBeg')
    else:
        f = WageForm(request.POST, instance = param)
        f.fields['period'].queryset = Period.objects.filter(user = request.user.id).order_by('-dBeg')
        if f.is_valid():
            f.save()

    context = get_base_context(request)
    context['title'] = _('Wage')
    context['form'] = f
    context['tree'] = BuildTree(request.user, 0, param.d_scan())
    context['stat_headers'] = ['Period', 'Depart', 'DepHist', 'Post', 'Employee', 'FioHist', 'Child', 'Appoint', 'Education', 'EmplPer', 'PayTitle', 'Payment']
    context['stat_values'] = get_stat()
    template = loader.get_template('wage/index.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
#              TREE
#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
def tree(request, pk):
    depart = Depart.objects.get(id = pk)
    if (depart != None):
        depart.is_open = not depart.is_open
        depart.save()
    return HttpResponseRedirect(reverse('wage:index'))

decorators = [login_required(login_url='account:login'), permission_required('wage.view_person')]


#----------------------------------
#              DEPART
#----------------------------------
@method_decorator(decorators, name='dispatch')
class DepartDetailView(UpdateView):
    model = Depart
    fields = ['name', 'sort']
    template_name = 'wage/depart.html'

"""
@login_required(login_url='account:login')
@permission_required('wage.view_person')
def depart(request, pk):
    depart = get_object_or_404(Depart.objects.get(id = pk))

    if (request.method != 'POST'):
        f = DepartForm(instance = depart)
    else:
        f = DepartForm(request.POST, instance = depart)
        if f.is_valid():
            f.save()

    context = get_base_context(request)
    context['title'] = _('Department')
    context['dep_form'] = f
    context['tree'] = BuildTree(request.user, 0, get_param(request.user).d_scan())
    template = loader.get_template('wage/depart.html')
    return HttpResponse(template.render(context, request))

"""

#----------------------------------
#              EMPLOYEE
#----------------------------------
@method_decorator(decorators, name='dispatch')
class EmployeeDetailView(UpdateView):
    model = Employee
    fields = ['user', 'login', 'fio', 'sort', 'email', 'passw', 'born', 'phone', 'addr', 'info']
    template_name = 'wage/employee.html'

"""
@login_required(login_url='account:login')
@permission_required('wage.view_person')
def employee(request, pk):
    context = get_base_context(request)
    context['title'] = _('Employee')
    template = loader.get_template('wage/employee.html')
    return HttpResponse(template.render(context, request))
"""

#----------------------------------
#              CLEAR
#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
def clear(request):
    delete_all()
    return HttpResponseRedirect(reverse('wage:index'))


#----------------------------------
#              IMPORT
#----------------------------------
@login_required(login_url='account:login')
@permission_required('wage.view_person')
def xml_import(request):
    imp_data  = []
    imp_errors = []
    import_all(request.user, imp_data, imp_errors)
    return HttpResponseRedirect(reverse('wage:index'))
    """
    template = loader.get_template('wage/import_result.html')
    context = {
        'xml': imp_data,
        'err': imp_errors,
        'xml_len': len(imp_data),
        'err_len': len(imp_errors),
        }
    return HttpResponse(template.render(context, request))
    """

    