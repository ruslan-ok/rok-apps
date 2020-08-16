from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.core.paginator import Paginator

from hier.models import Folder
from hier.utils import get_base_context, check_file_for_content, process_common_commands
from .models import Entry, Params
from .forms import EntryForm, ParamsForm
from .imp_xml import delete_all, import_all

#----------------------------------
# Entry
#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def entry_list(request, folder_id):
    process_common_commands(request)

    for e in Folder.objects.filter(user = request.user.id, node = folder_id, model_name = 'store:entry').exclude(content_id = 0):
        e.model_name = 'store:entry_form'
        e.save()

    for e in Folder.objects.filter(user = request.user.id, node = folder_id, content_id = 0, model_name = 'store:entry'):
        e.model_name = 'store:entry_list'
        e.save()

    if Folder.objects.filter(user = request.user.id, node = folder_id, content_id = 0).exists():
        return HttpResponseRedirect(reverse('hier:folder_dir', args = [folder_id]))

    if Folder.objects.filter(user = request.user.id, node = folder_id).exclude(content_id = 0).exclude(model_name = 'store:entry_form').exists():
        return HttpResponseRedirect(reverse('hier:folder_dir', args = [folder_id]))

    data = []
    if request.method != 'GET':
        files = Folder.objects.filter(user = request.user.id, node = folder_id).order_by('code', 'name')
        for file in files:
            add_entry(data, file.id, Entry.objects.filter(user = request.user.id, id = file.content_id).get())
        page_number = 1
    else:
        page_number = request.GET.get('page')
        query = request.GET.get('q')
        if query:
            lookups = Q(title__icontains=query) | Q(username__icontains=query) | Q(url__icontains=query) | Q(notes__icontains=query)
            for entry in Entry.objects.filter(user = request.user.id, actual = 1).filter(lookups).distinct():
                if Folder.objects.filter(user = request.user.id, node = folder_id, model_name = 'store:entry', content_id = entry.id).exists(): 
                    file = Folder.objects.filter(user = request.user.id, node = folder_id, model_name = 'store:entry', content_id = entry.id).get()
                    add_entry(data, file.id, entry)
        else:
            files = Folder.objects.filter(user = request.user.id, node = folder_id).order_by('code', 'name')
            for file in files:
                if Entry.objects.filter(user = request.user.id, id = file.content_id).exists():
                    add_entry(data, file.id, Entry.objects.filter(user = request.user.id, id = file.content_id).get())
                else:
                    data.append({ 'folder_id': file.id,
                                  'id': 0,
                                  'title': file.name })

    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    
    stat = []
    stat.append(['Entry', len(Entry.objects.all())])

    context = get_base_context(request, folder_id, 0, '', 'content_list')
    context['total'] = len(data)
    context['page_obj'] = page_obj
    context['stat'] = stat
    context['debug'] = 'Entry_Qty = ' + str(len(Entry.objects.all()))
    template = loader.get_template('store/entry_list.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
def add_entry(data, file_id, entry):
    data.append({ 'folder_id': file_id,
                  'id': entry.id,
                  'title': entry.title,
                  'username': entry.username,
                  'value': entry.value,
                  'url': entry.url,
                  'have_notes': entry.have_notes() })

#----------------------------------
def entry_add(request, folder_id):
    if (request.method == 'POST'):
        form = EntryForm(request.POST)
    else:
        form = EntryForm(initial = {'name': '',
                                    'value': make_random_string(request.user),
                                    'uuid': '',
                                    })
    return show_page_form(request, folder_id, 0, _('create a new entry'), 'entry', form)

#----------------------------------
def entry_form(request, folder_id, content_id):
    process_common_commands(request)
    if not Entry.objects.filter(id = content_id, user = request.user.id).exists():
        data_file = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
        if (data_file.model_name == 'store:entry'):
            data_file.content_id = 0
            data_file.save()
        return HttpResponseRedirect(reverse('hier:folder_form', args = [folder_id]))
    data = get_object_or_404(Entry.objects.filter(id = content_id, user = request.user.id))
    query = request.GET.get('q')
    page = request.GET.get('page')
    if (request.method == 'POST'):
        form = EntryForm(request.POST, instance = data)
    else:
        form = EntryForm(instance = data)
    list_filter = ''
    if query and page:
        list_filter = '?q=' + query + '&page=' + page
    return show_page_form(request, folder_id, content_id, _('entry') + ' "' + data.title + '"', 'entry', form, list_filter = list_filter)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def entry_del(request, folder_id, content_id):
    data_file = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    node_id = data_file.node
    entry = get_object_or_404(Entry.objects.filter(id = content_id, user = request.user.id))
    entry.delete()
    data_file.delete()
    return HttpResponseRedirect(reverse('store:entry_list', args = [node_id]))

#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def entry_move(request, folder_id, content_id, to_folder):
    data_file = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    dst_folder = get_object_or_404(Folder.objects.filter(id = to_folder, user = request.user.id))
    data_file.node = to_folder
    data_file.save()
    return HttpResponseRedirect(reverse('hier:folder_list', args = [to_folder]))

              
#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def show_page_list(request, folder_id, title, name, data, total = 0):
    context = get_base_context(request, folder_id, 0, title, 'content_list')
    context['total'] = total
    context[name + 's'] = data
    template = loader.get_template('store/' + name + '_list.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def show_page_form(request, folder_id, content_id, title, name, form, extra_context = {}, list_filter = ''):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.user = request.user
            form.save()
            redirect_id = folder_id
            if (name == 'entry'):
                redirect_id = check_file_for_content(request.user, folder_id, data.id, data.title, data.title, content_id == 0)
                if (content_id == 0):
                    folder = Folder.objects.filter(user = request.user.id, node = redirect_id, content_id = data.id).get()
                    folder.model_name = 'store:entry_form'
                    folder.save()
            if (name == 'entry') or (name == 'param'):
                return HttpResponseRedirect(reverse('store:entry_list', args = [redirect_id]) + list_filter)
            else:
                return HttpResponseRedirect(reverse('store:' + name + '_list', args = [redirect_id]))
    context = get_base_context(request, folder_id, content_id, title, form = form)
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
# Parameters
#----------------------------------
def get_params(user):
    if (len(Params.objects.filter(user = user.id)) > 0):
        return Params.objects.filter(user = user.id)[0]
    else:
        return Params.objects.create(user = user)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def entry_param(request, folder_id):
    data = get_params(request.user)
    if (request.method == 'POST'):
        form = ParamsForm(request.POST, instance = data)
    else:
        form = ParamsForm(instance = data)
    return show_page_form(request, folder_id, 0, _('parameters'), 'param', form)

#----------------------------------
# Delete all data!
#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def clear(request, folder_id):
    delete_all()
    return HttpResponseRedirect(reverse('store:entry_list', args = [folder_id]))

#----------------------------------
# Import from XML
#----------------------------------
@login_required(login_url='account:login')
@permission_required('store.view_entry')
#----------------------------------
def xml_import(request, folder_id):
    imp_data  = []
    imp_errors = []
    import_all(request.user, imp_data, imp_errors)

    stat = []
    stat.append(['Entry', len(Entry.objects.all())])

    context = get_base_context(request, folder_id, 0, _('entries'))
    context['stat'] = stat
    context['imp_data'] = imp_data
    context['imp_errors'] = imp_errors
    template_file = 'store/entry_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

              
