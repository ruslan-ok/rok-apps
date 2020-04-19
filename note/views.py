from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from hier.utils import get_base_context
from .forms import ListForm, NoteForm, ViewForm
from .models import List, Note, View, Filter, Param

 

#----------------------------------
# Index
#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def index(request):
    if Param.objects.filter(user = request.user.id).exists():
        param = Param.objects.filter(user = request.user)[0]
    else:
        param = Param.objects.create(user = request.user)
    
    sets = []
    title = 'Доска'
    pk = 0
    is_chrono = False
    if param.view:
        is_chrono = param.view.chrono
        title = param.view.name
        pk = param.view.id
        check_chrono(param.view)
        for filter in Filter.objects.filter(view = param.view, entity = 1).order_by('npp'):
            if List.objects.filter(user = request.user.id, id = filter.value).exists():
                list = List.objects.filter(user = request.user.id, id = filter.value).get()
                if is_chrono:
                    sets.append([list, Note.objects.filter(user = request.user.id, list = list.id).order_by('-publ'),])
                else:
                    sets.append([list, Note.objects.filter(user = request.user.id, list = list.id).order_by('code', 'name'),])
    else:
        lists = List.objects.filter(user = request.user.id).order_by('code', 'name')
        for list in lists:
            sets.append([list, Note.objects.filter(user = request.user.id, list = list.id).order_by('code', 'name'),])
    
    context = get_base_context(request, 0, pk, title, 'note')
    context['views'] = View.objects.filter(user = request.user.id).order_by('code', 'name')
    context['sets'] = sets
    if is_chrono:
        template_file = 'note/news.html'
    else:
        template_file = 'note/index.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
# View set
#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def view_set(request, pk):
    view = get_object_or_404(View.objects.filter(user = request.user.id, id = pk))

    if Param.objects.filter(user = request.user.id).exists():
        param = Param.objects.filter(user = request.user)[0]
        param.view = view
        param.save()
    else:
        param = Param.objects.create(user = request.user, view = view)

    return HttpResponseRedirect(reverse('note:index'))


#----------------------------------
# List
#----------------------------------
def list_list(request):
    data = List.objects.filter(user = request.user.id).order_by('code', 'name')
    return show_page_list(request, 'Списки', 'list', data)

#----------------------------------
def list_add(request):
    if (request.method == 'POST'):
        form = ListForm(request.POST)
    else:
        form = ListForm(initial = {'name': '', 'code': '', 'color': '#b6e9e3',})
    return show_page_form(request, 0, 'Список', 'list', form)

#----------------------------------
def list_form(request, pk):
    data = get_object_or_404(List.objects.filter(id = pk, user = request.user.id))
    if (request.method == 'POST'):
        form = ListForm(request.POST, instance = data)
    else:
        form = ListForm(instance = data)
    return show_page_form(request, pk, 'Список', 'list', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def list_del(request, pk):
    List.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('note:list_list'))


#----------------------------------
# Note
#----------------------------------
def note_list(request):
    data = Note.objects.filter(user = request.user.id).order_by('code', 'name')
    return show_page_list(request, 'Заметки', 'note', data)

#----------------------------------
def note_add(request):
    lst = int(request.GET.get('list'))
    list = get_object_or_404(List.objects.filter(id = lst, user = request.user.id))
    if (request.method == 'POST'):
        form = NoteForm(request.user, request.POST)
    else:
        new_code = get_next_code(request.user.id, list)
        form = NoteForm(request.user, initial = {'name': '', 'code': new_code, 'list': list,})
    return show_page_form(request, 0, 'Заметка', 'note', form, get_del_or_ready(list))

#----------------------------------
def note_form(request, pk):
    data = get_object_or_404(Note.objects.filter(id = pk, user = request.user.id))
    if (request.method == 'POST'):
        form = NoteForm(request.user, request.POST, instance = data)
    else:
        form = NoteForm(request.user, instance = data)

    return show_page_form(request, pk, 'Заметка', 'note', form, get_del_or_ready(data.list))

#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def note_del(request, pk):
    data = get_object_or_404(Note.objects.filter(id = pk, user = request.user.id))
    if (data.list.name == 'Готово'):
        Note.objects.get(id = pk).delete()
    else:
        ready = get_ready_list(request.user)
        if ready:
            data.list = ready
            data.save()
        else:
            ready = List.objects.filter(user = request.user.id, code = 'Общий', name = 'Готово')
            if ready.exists():
                data.list = ready[0]
                data.save()
            else:
                Note.objects.get(id = pk).delete()
    
    return HttpResponseRedirect(reverse('note:index'))

#----------------------------------
# View
#----------------------------------
def view_list(request):
    data = View.objects.filter(user = request.user.id).order_by('code', 'name')
    return show_page_list(request, 'Представления', 'view', data)

#----------------------------------
def view_add(request):
    if (request.method == 'POST'):
        form = ViewForm(request.POST)
    else:
        form = ViewForm()
    return show_page_view(request, 0, 'Представление', 'view', form)

#----------------------------------
def view_form(request, vw):
    data = get_object_or_404(View.objects.filter(id = vw, user = request.user.id))
    if (request.method == 'POST'):
        form = ViewForm(request.POST, instance = data)
    else:
        form = ViewForm(instance = data)
    return show_page_view(request, vw, 'Представление', 'view', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def view_del(request, vw):
    View.objects.get(id = vw).delete()
    return HttpResponseRedirect(reverse('note:view_list'))



#----------------------------------
# Chrono
#----------------------------------
def chrono_add(request):
    lst = int(request.GET.get('list'))
    list = get_object_or_404(List.objects.filter(id = lst, user = request.user.id))
    if (request.method == 'POST'):
        form = NoteForm(request.user, request.POST)
    else:
        new_code = get_next_code(request.user.id, list)
        form = NoteForm(request.user, initial = {'name': '', 'code': new_code, 'list': list, 'chrono': datetime.now()})
    return show_page_form(request, 0, 'Новость', 'chrono', form)

#----------------------------------
def chrono_form(request, pk):
    data = get_object_or_404(Note.objects.filter(id = pk, user = request.user.id))
    if (request.method == 'POST'):
        form = NoteForm(request.user, request.POST, instance = data)
    else:
        form = NoteForm(request.user, instance = data)

    return show_page_form(request, pk, 'Новость', 'chrono', form)

#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def chrono_del(request, pk):
    data = get_object_or_404(Note.objects.filter(id = pk, user = request.user.id))
    ready = List.objects.filter(user = request.user.id, code = 'Общий', name = 'Готово')
    if ready.exists():
        data.list = ready[0]
        data.save()
    else:
        Note.objects.get(id = pk).delete()
    
    return HttpResponseRedirect(reverse('note:index'))





#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def view_list_add(request, vw, lst):
    view = get_object_or_404(View.objects.filter(id = vw, user = request.user.id))
    if not Filter.objects.filter(view = view, entity = 1, value = lst):    
        last = Filter.objects.filter(view = view, entity = 1).order_by('npp')[0:1]
        new_npp = 1
        if last:
            new_npp = last[0].npp + 1
        Filter.objects.create(view = view, entity = 1, npp = new_npp, value = lst)
    return HttpResponseRedirect(reverse('note:view_form', args=(vw,)))

#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def view_list_del(request, vw, lst):
    view = get_object_or_404(View.objects.filter(id = vw, user = request.user.id))
    list = get_object_or_404(Filter.objects.filter(view = view, entity = 1, value = lst))
    list.delete()
    return HttpResponseRedirect(reverse('note:view_form', args=(vw,)))



#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def show_page_list(request, title, name, data):
    context = get_base_context(request, 0, 0, title, 'note')
    context[name + 's'] = data
    template = loader.get_template('note/' + name + '_list.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def show_page_form(request, pk, title, name, form, extra_context = {}):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.user = request.user
            form.save()
            if (name == 'note') or (name == 'chrono'):
                return HttpResponseRedirect(reverse('note:index'))
            else:
                return HttpResponseRedirect(reverse('note:' + name + '_list'))
    context = get_base_context(request, 0, pk, title, 'note')
    context['form'] = form
    context.update(extra_context)
    template = loader.get_template('note/' + name + '_form.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
@permission_required('note.view_note')
#----------------------------------
def show_page_view(request, pk, title, name, form):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.user = request.user
            form.save()
            return HttpResponseRedirect(reverse('note:' + name + '_list'))
    context = get_base_context(request, 0, pk, title, 'note')
    context['form'] = form
    sel = []
    avl = []
    for list in List.objects.filter(user = request.user.id).order_by('code', 'name'):
        if Filter.objects.filter(view = pk, entity = 1, value = list.id).exists():
            sel.append(list)
        else:
            avl.append(list)
    context['selected_list'] = sel
    context['available_list'] = avl
    template = loader.get_template('note/' + name + '_form.html')
    return HttpResponse(template.render(context, request))



#----------------------------------
# Инкрементация кода для новой заметки
#----------------------------------
def get_next_code(user, list):
    new_code = '1'
    last = Note.objects.filter(user = user, list = list).order_by('-code')[0:1]
    if (len(last) > 0):
        try:
            num_code = int(last[0].code)
            num_code = num_code + 1
            new_code = str(num_code)
        except ValueError:
            pass
    return new_code

#----------------------------------
# Какую кнопку показать для удаления заметки
#----------------------------------
def get_del_or_ready(list):
    if (list.name != 'Готово'):
        ready = get_ready_list(list.user)
        if ready:
            return dict(del_or_ready = 'Готово', del_color = 'w3-green')

    return dict(del_or_ready = 'Удалить', del_color = 'w3-red')


#----------------------------------
# Поиск списка "Готово" в текущем представлении
#----------------------------------
def get_ready_list(user):
    param = get_object_or_404(Param.objects.filter(user = user))
    filters = Filter.objects.filter(view = param.view.id, entity = 1).order_by('npp')
    for filter in filters:
        if List.objects.filter(user = param.user.id, id = filter.value).exists():
            list_in_view = List.objects.filter(user = param.user.id, id = filter.value).get()
            if (list_in_view.name == 'Готово'):
                return list_in_view
    return None


#----------------------------------
# У представления с атрибутом chrono должен быть один специальный список
#----------------------------------
def check_chrono(view):
    if view.chrono:
        if not Filter.objects.filter(view = view, entity = 1).exists():
            list = List.objects.create(user = view.user, code = view.name, name = 'Add item')
            Filter.objects.create(view = view, entity = 1, value = list.id)






