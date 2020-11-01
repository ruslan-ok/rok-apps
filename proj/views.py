import locale
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q

from hier.utils import get_base_context_ext, process_common_commands, extract_get_params, sort_data
from hier.params import set_sort_mode, toggle_sort_dir, get_search_mode, get_search_info, set_restriction, set_article_kind, set_article_visible
from hier.models import get_app_params
from hier.aside import Fix, Sort
from todo.utils import nice_date
from .models import app_name, Projects, set_active, Expenses, s_proj_summary
from .forms import ProjectForm, ExpenseForm

items_per_page = 10

SORT_MODE_DESCR = {
    '': '',
    'name': _('sort by name'),
    'date': _('sort by date'),
    'kontr': _('sort by contractor'),
    'text': _('sort by description'),
    'created': _('sort by creation date'),
    'last_mod': _('sort by last modification date'),
}

#----------------------------------
def get_title(restriction, project):
    if (restriction == 'project'):
        return _('projects').capitalize()
    if (restriction == 'expense'):
        return '{} [{}]'.format(_('expenses').capitalize(), project.name)
    return 'unknown restriction: ' + str(restriction)

#----------------------------------
def get_template_file(restriction):
    if (restriction == 'project'):
        return 'proj/project.html'
    if (restriction == 'expense'):
        return 'proj/expense.html'
    return 'proj/expense.html'

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def main(request):
    app_param = get_app_params(request.user, app_name)
    if (app_param.restriction != 'project') and (app_param.restriction != 'expense'):
        set_restriction(request.user, app_name, 'expense')
        return HttpResponseRedirect(reverse('proj:main') + extract_get_params(request))

    if not Projects.objects.filter(user = request.user.id, active = True).exists():
        set_restriction(request.user, app_name, 'project')
        return HttpResponseRedirect(reverse('proj:main'))

    project = Projects.objects.filter(user = request.user.id, active = True).get()

    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('proj:main') + extract_get_params(request))

    if process_sort_commands(request, app_name):
        return HttpResponseRedirect(reverse('proj:main') + extract_get_params(request))

    # для трансляции строкового представления дат, в частности в item_info
    locale.setlocale(locale.LC_CTYPE, request.LANGUAGE_CODE)
    locale.setlocale(locale.LC_TIME, request.LANGUAGE_CODE)

    form = None
    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item-add' in request.POST):
            if (app_param.restriction == 'project'):
                item_id = add_project(request)
            if (app_param.restriction == 'expense'):
                item_id = add_expense(request, project)
            return HttpResponseRedirect(reverse('proj:item_form', args = [item_id]))
        if ('item-in-list-select' in request.POST) and (app_param.restriction == 'project'):
            pk = request.POST['item-in-list-select']
            if pk:
                set_active(request.user.id, pk)
                return HttpResponseRedirect(reverse('proj:item_form', args = [pk]))

    app_param, context = get_base_context_ext(request, app_name, 'main', get_title(app_param.restriction, project))

    redirect = False

    if app_param.article:
        valid_article = False
        if (app_param.restriction == 'project'):
            valid_article = Projects.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if (app_param.restriction == 'expense'):
            valid_article = Expenses.objects.filter(id = app_param.art_id, direct = project).exists()
        if valid_article:
            if (app_param.restriction == 'project'):
                item = get_object_or_404(Projects.objects.filter(user = request.user.id, id = app_param.art_id))
                disable_delete = item.active or Expenses.objects.filter(direct = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, None, item, disable_delete)
            if (app_param.restriction == 'expense'):
                item = get_object_or_404(Expenses.objects.filter(id = app_param.art_id, direct = project))
                redirect = edit_item(request, context, app_param.restriction, project, item)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('proj:main') + extract_get_params(request))

    fixes = []
    fixes.append(Fix('project', _('projects').capitalize(), 'todo/icon/myday.png', 'projects/', len(Projects.objects.filter(user = request.user.id))))
    fixes.append(Fix('expense', _('expenses').capitalize(), 'rok/icon/cost.png', 'expenses/', len(Expenses.objects.filter(direct = project))))
    context['fix_list'] = fixes

    sorts = []
    if (app_param.restriction == 'project'):
        sorts.append(Sort('name',  _('by name').capitalize(), 'todo/icon/sort.png'))
    if (app_param.restriction == 'expense'):
        sorts.append(Sort('date', _('by date').capitalize(), 'rok/icon/application.png'))
        sorts.append(Sort('kontr', _('by contractor').capitalize(), 'rok/icon/car.png'))
        sorts.append(Sort('text', _('by description').capitalize(), 'rok/icon/note.png'))
    sorts.append(Sort('created', _('by creation date').capitalize(), 'todo/icon/created.png'))
    sorts.append(Sort('lmod',  _('by last modification date').capitalize(), 'todo/icon/planned.png'))
    context['sort_options'] = sorts

    if app_param.sort:
        context['sort_mode'] = SORT_MODE_DESCR[app_param.sort].capitalize()

    context['without_lists'] = True
    context['hide_important'] = True
    if (app_param.restriction == 'project'):
        context['add_item_placeholder'] = _('add new project').capitalize()
    if (app_param.restriction == 'expense'):
        context['hide_add_item_input'] = True
        context['hide_selector'] = True
        context['title_info'] = s_proj_summary(project.id)

    query = None
    page_number = 1
    if (request.method == 'GET'):
        query = request.GET.get('q')
        page_number = request.GET.get('page')
    context['search_info'] = get_search_info(query)
    data = filtered_sorted_list(request.user, app_param, project, query)
    paginator = Paginator(data, items_per_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)
    context['search_info'] = get_search_info(query)
    template = loader.get_template(get_template_file(app_param.restriction))
    return HttpResponse(template.render(context, request))

def item_form(request, pk):
    set_article_kind(request.user, app_name, '', pk)
    return HttpResponseRedirect(reverse('proj:main') + extract_get_params(request))

def go_projects(request):
    set_restriction(request.user, app_name, 'project')
    return HttpResponseRedirect(reverse('proj:main'))

def go_expenses(request):
    set_restriction(request.user, app_name, 'expense')
    return HttpResponseRedirect(reverse('proj:main'))

#----------------------------------
def filtered_list(user, restriction, project, query = None):
    if (restriction == 'project'):
        data = Projects.objects.filter(user = user.id)
    elif (restriction == 'expense'):
        data = Expenses.objects.filter(direct = project)
    else:
        data = []

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode != 1):
        return data

    if (restriction == 'project'):
        lookups = Q(name__icontains=query)
    elif (restriction == 'expense'):
        lookups = Q(kontr__icontains=query) | Q(text__icontains=query)
    else:
        return data

    return data.filter(lookups).distinct()

def filtered_sorted_list(user, app_param, project, query):
    data = filtered_list(user, app_param.restriction, project, query)
    return sort_data(data, app_param.sort, app_param.reverse)

#----------------------------------
def process_sort_commands(request, app):
    if ('sort-delete' in request.POST):
        set_sort_mode(request.user, app, '')
        return True
    if ('sort-name' in request.POST):
        set_sort_mode(request.user, app_name, 'name')
        return True
    if ('sort-date' in request.POST):
        set_sort_mode(request.user, app_name, 'date')
        return True
    if ('sort-kontr' in request.POST):
        set_sort_mode(request.user, app_name, 'kontr')
        return True
    if ('sort-text' in request.POST):
        set_sort_mode(request.user, app_name, 'text')
        return True
    if ('sort-created' in request.POST):
        set_sort_mode(request.user, app_name, 'created')
        return True
    if ('sort-lmod' in request.POST):
        set_sort_mode(request.user, app_name, 'last_mod')
    if ('sort-direction' in request.POST):
        toggle_sort_dir(request.user, app)
        return True
    return False

#----------------------------------
def add_project(request):
    item = Projects.objects.create(user = request.user, name = request.POST['item_add-name'])
    return item.id

def add_expense(request, project):
    item = Expenses.objects.create(direct = project, rate = 0)
    return item.id

#----------------------------------
def edit_item(request, context, restriction, project, item, disable_delete = False):
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            delete_item(request, item, disable_delete)
            return True
        if ('item-save' in request.POST):
            if (restriction == 'project'):
                form = ProjectForm(request.POST, instance = item)
            elif (restriction == 'expense'):
                form = ExpenseForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                if (restriction == 'cars'):
                    data.user = request.user
                else:
                    data.direct = project
                form.save()
                return True

    if not form:
        if (restriction == 'project'):
            form = ProjectForm(instance = item)
        elif (restriction == 'expense'):
            form = ExpenseForm(instance = item)

    context['form'] = form
    context['ed_item'] = item
    context['item_info'] = str(_('created:').capitalize()) + nice_date(item.created.date())
    return False

#----------------------------------
def delete_item(request, item, disable_delete = False):
    if disable_delete:
        return False
    item.delete()
    set_article_visible(request.user, app_name, False)
    return True

    

