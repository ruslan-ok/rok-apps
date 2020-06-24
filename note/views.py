from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from hier.models import Folder
from hier.utils import get_base_context, check_file_for_content, is_in_trash, put_in_the_trash, get_folder_id, process_common_commands

from .models import Note
from .forms import NoteForm
from .utils import get_ready_folder

#----------------------------------
# Note
#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def note_list(request, folder_id):
    process_common_commands(request)
    node = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    data = Folder.objects.filter(user = request.user.id, node = folder_id).order_by('code', 'name')

    sets = []
    for file in data:
        sets.append([file, Folder.objects.filter(user = request.user.id, node = file.id).order_by('code', 'name'), can_create_note(file.id, file.content_id),])
    
    context = get_base_context(request, folder_id, 0, node.name, 'content_list')
    context['sets'] = sets
    template_file = 'note/note_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def note_down(request, folder_id):
    folder = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    node = get_object_or_404(Folder.objects.filter(id = folder.node, user = request.user.id))
    if not node.is_open:
        node.is_open = True
        node.save()
    if folder.content_id:
        return HttpResponseRedirect(reverse('note:note_form', args = [folder_id, folder.content_id]))
    else:
        return HttpResponseRedirect(reverse('note:note_list', args = [folder_id]))

#----------------------------------
def note_add(request, folder_id):
    if (request.method == 'POST'):
        form = NoteForm(request.POST)
    else:
        new_code = get_next_code(request.user.id, folder_id)
        form = NoteForm(initial = {'name': '', 'code': new_code, })
    return show_page_form(request, folder_id, 0, _('create a new note'), 'note', form)

#----------------------------------
def note_form(request, folder_id, content_id):
    if not Note.objects.filter(id = content_id, user = request.user.id).exists():
        return HttpResponseRedirect(reverse('hier:folder_form', args = [folder_id]))
    note_file = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    data = Note.objects.filter(id = content_id, user = request.user.id).get()
    if (request.method == 'POST'):
        form = NoteForm(request.POST, instance = data)
    else:
        form = NoteForm(instance = data)

    return show_page_form(request, folder_id, content_id, _('note') + ' "' + data.name + '"', 'note', form)


#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def note_move(request, folder_id, content_id, to_folder):
    note_file = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    dst_folder = get_object_or_404(Folder.objects.filter(id = to_folder, user = request.user.id))
    note_file.node = to_folder
    note_file.save()
    return HttpResponseRedirect(reverse('hier:folder_list', args = [dst_folder.node]))


#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def note_del(request, folder_id, content_id):
    note_file = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    node_id = note_file.node
    if is_in_trash(folder_id):
        note = get_object_or_404(Note.objects.filter(id = content_id, user = request.user.id))
        note.delete()
        note_file.delete()
    else:
        ready = get_ready_folder(request.user.id, folder_id)
        if not ready:
            put_in_the_trash(request.user, folder_id)
        else:
            if (ready.id == node_id):
                put_in_the_trash(request.user, folder_id)
            else:
                # Put in the Ready-Folder
                note_file.node = ready.id
                note_file.save()
                node_id = ready.node

    return HttpResponseRedirect(reverse('hier:folder_list', args = [node_id]))

#----------------------------------
# News
#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def news_list(request, folder_id):
    process_common_commands(request)
    data = Folder.objects.filter(user = request.user.id, node = folder_id).order_by('-creation')
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
        query = request.GET.get('q')
        if query:
            lookups = Q(name__icontains=query) | Q(code__icontains=query) | Q(descr__icontains=query) | Q(publ__icontains=query)
            filtered_news = Note.objects.filter(user = request.user.id).filter(lookups).distinct()
            data = Folder.objects.filter(user = request.user.id, node = folder_id, content_id__in = filtered_news).order_by('-creation')
            
    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    
    news = []
    for entry in page_obj:
        note = Note.objects.filter(user = request.user.id, id = entry.content_id).get()
        news.append([entry, note])

    context = get_base_context(request, folder_id, 0, _('news'), 'content_list')
    context['news'] = news
    context['total'] = len(data)
    context['page_obj'] = page_obj
    template_file = 'note/news_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def news_add(request, folder_id):
    node = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    if (request.method == 'POST'):
        form = NoteForm(request.POST)
    else:
        new_code = get_next_code(request.user.id, folder_id)
        form = NoteForm(initial = {'name': '', 'code': new_code, 'publ': datetime.now()})
    return show_page_form(request, folder_id, 0, _('create new news'), 'news', form)

#----------------------------------
def news_form(request, folder_id, content_id):
    data = get_object_or_404(Note.objects.filter(id = content_id, user = request.user.id))
    if (request.method == 'POST'):
        form = NoteForm(request.POST, instance = data)
    else:
        form = NoteForm(instance = data)

    return show_page_form(request, folder_id, content_id, _('news') + ' "' + data.name + '"', 'news', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def news_del(request, folder_id, content_id):
    file = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    node_id = file.node
    data = get_object_or_404(Note.objects.filter(id = content_id, user = request.user.id))
    if is_in_trash(folder_id):
        data.delete()
        file.delete()
    else:
        put_in_the_trash(request.user, folder_id)
    return HttpResponseRedirect(reverse('note:news_list', args = [node_id]))

#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def show_page_form(request, folder_id, content_id, title, name, form, extra_context = {}):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.user = request.user
            form.save()
            redirect_id = check_file_for_content(request.user, folder_id, data.id, data.name, data.code, content_id == 0)
            return HttpResponseRedirect(reverse('hier:folder_list', args = [redirect_id]))
    context = get_base_context(request, folder_id, content_id, title, form = form)
    context.update(extra_context)
    template = loader.get_template('note/' + name + '_form.html')
    return HttpResponse(template.render(context, request))


#----------------------------------
# Нужно ли добавлять заметку по клиек на папке
#----------------------------------
def can_create_note(folder_id, content_id):
    if content_id:
        ret = False
    else:
        ret = True
        for file in Folder.objects.filter(node = folder_id):
            if not file.content_id:
                ret = False
                break
    return ret

#----------------------------------
# Инкрементация кода для новой заметки
#----------------------------------
def get_next_code(user_id, list_folder_id):
    new_code = '1'
    last = Folder.objects.filter(user = user_id, node = list_folder_id).order_by('-code')[0:1]
    if (len(last) > 0):
        try:
            num_code = int(last[0].code)
            num_code = num_code + 1
            new_code = str(num_code)
        except ValueError:
            pass
    return new_code



