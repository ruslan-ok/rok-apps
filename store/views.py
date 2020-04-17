from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.core.paginator import Paginator
from .models import Group, Entry, History, Params
from .forms import GroupForm, EntryForm, FilterForm, ParamsForm
from .imp_xml import delete_all, import_all

#----------------------------------
# Index
#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def index(request):
    params = get_params(request.user)
    if request.method != 'GET':
        data = Entry.objects.filter(user = request.user.id, actual = 1).order_by('title')
        page_number = 1
    else:
        page_number = request.GET.get('page')
        query = request.GET.get('q')
        if (not query):
            data = Entry.objects.filter(user = request.user.id, actual = 1).order_by('title')
        else:
            """
            _mutable = request.GET._mutable
            request.GET._mutable = True
            request.GET['q'] = ''
            request.GET._mutable = _mutable
            """
            lookups = Q(title__icontains=query) | Q(username__icontains=query) | Q(url__icontains=query) | Q(notes__icontains=query)
            data = Entry.objects.filter(user = request.user.id, actual = 1).filter(lookups).distinct()
        group_id = request.GET.get('group')
        if not group_id:
            params.group = None
        else:
            params.group = get_object_or_404(Group.objects.filter(id = group_id, user = request.user.id))
            data = data.filter(group = group_id)
        params.save()
    
    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    
    stat = []
    stat.append(['Group', len(Group.objects.all())])
    stat.append(['Entry', len(Entry.objects.all())])
    stat.append(['History', len(History.objects.all())])

    context = get_base_context(request)
    context['title'] = _('entries').capitalize()
    context['total'] = len(data)
    context['page_obj'] = page_obj
    context['stat'] = stat
    context['filter'] = FilterForm(instance = params)
    template = loader.get_template('store/index.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
# Parameters
#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def param_form(request):
    data = get_params(request.user)
    if (request.method == 'POST'):
        form = ParamsForm(request.POST, instance = data)
    else:
        form = ParamsForm(instance = data)
    return show_page_form(request, 0, _('parameters').capitalize(), 'param', form)

#----------------------------------
# Delete all data!
#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def clear(request):
    delete_all()
    return HttpResponseRedirect(reverse('store:index'))

#----------------------------------
# Import from XML
#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def xml_import(request):
    imp_data  = []
    imp_errors = []
    import_all(request.user, imp_data, imp_errors)

    stat = []
    stat.append(['Group', len(Group.objects.all())])
    stat.append(['Entry', len(Entry.objects.all())])
    stat.append(['History', len(History.objects.all())])

    context = get_base_context(request)
    context['title'] = _('entries').capitalize()
    context['stat'] = stat
    context['imp_data'] = imp_data
    context['imp_errors'] = imp_errors
    template_file = 'store/index.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

              
#----------------------------------
# Group
#----------------------------------
def group_list(request):
    data = Group.objects.filter(user = request.user.id).order_by('code', 'name')
    total = len(Group.objects.filter(user = request.user.id))
    return show_page_list(request, _('groups').capitalize(), 'group', data, total)

#----------------------------------
def group_add(request):
    if (request.method == 'POST'):
        form = GroupForm(request.POST)
    else:
        form = GroupForm(initial = {'name': '',})
    return show_page_form(request, 0, _('group').capitalize(), 'group', form)

#----------------------------------
def group_form(request, pk):
    data = get_object_or_404(Group.objects.filter(id = pk, user = request.user.id))
    if (request.method == 'POST'):
        form = GroupForm(request.POST, instance = data)
    else:
        form = GroupForm(instance = data)
    return show_page_form(request, pk, _('group').capitalize(), 'group', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def group_del(request, pk):
    Group.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('store:group_list'))

              
#----------------------------------
# Entry
#----------------------------------
def entry_add(request):
    if (request.method == 'POST'):
        form = EntryForm(request.POST)
    else:
        form = EntryForm(initial = {'name': '',
                                    'value': make_random_string(request.user),
                                    'uuid': '',
                                    })
    return show_page_form(request, 0, _('entry').capitalize(), 'entry', form)

#----------------------------------
def entry_form(request, pk):
    data = get_object_or_404(Entry.objects.filter(id = pk, user = request.user.id))
    if (request.method == 'POST'):
        form = EntryForm(request.POST, instance = data)
    else:
        form = EntryForm(instance = data)
    return show_page_form(request, pk, _('entry').capitalize(), 'entry', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def entry_del(request, pk):
    Entry.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('store:index'))

              
#----------------------------------
# Контекст для любой страницы
#----------------------------------
def get_base_context(request):
    return { 'site_header': get_current_site(request).name, }

#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def show_page_list(request, title, name, data, total = 0):
    context = get_base_context(request)
    context['title'] = title
    context['total'] = total
    context[name + 's'] = data
    template = loader.get_template('store/' + name + '_list.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def show_page_form(request, pk, title, name, form, extra_context = {}):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.user = request.user
            form.save()
            if (name == 'entry') or (name == 'param'):
                return HttpResponseRedirect(reverse('store:index'))
            else:
                return HttpResponseRedirect(reverse('store:' + name + '_list'))
    context = get_base_context(request)
    context['title'] = title
    context['pk'] = pk
    context['form'] = form
    context.update(extra_context)
    template = loader.get_template('store/' + name + '_form.html')
    return HttpResponse(template.render(context, request))


#----------------------------------
def make_random_string(user):
    params = get_params(user)
    allowed_chars = ''
    
    if params.uc:
        allowed_chars = allowed_chars + 'ABCDEFGHJKLMNPQRSTUVWXYZ'
        if not params.ac:
            allowed_chars = allowed_chars + 'IO'
    
    if params.lc:
        allowed_chars = allowed_chars + 'abcdefghjkmnpqrstuvwxyz'
        if not params.ac:
            allowed_chars = allowed_chars + 'io'

    if params.dg:
        allowed_chars = allowed_chars + '23456789'
        if not params.ac:
            allowed_chars = allowed_chars + '10'

    if params.sp:
        allowed_chars = allowed_chars + '!@#$%^&*=+'

    if params.br:
        allowed_chars = allowed_chars + '()[]{}<>'
    
    if params.mi:
        allowed_chars = allowed_chars + '-'
    
    if params.ul:
        allowed_chars = allowed_chars + '_'

    if (allowed_chars == ''):
        allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*(-_=+)'

    return get_random_string(params.ln, allowed_chars)


#----------------------------------
def get_params(user):
    if (len(Params.objects.filter(user = user.id)) > 0):
        return Params.objects.filter(user = user.id)[0]
    else:
        return Params.objects.create(user = user)
