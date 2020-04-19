from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hier.models import File
from hier.forms import FileForm
from hier.utils import i_storage_type, rmtree, check_health, get_base_context
from store.models import Group, Entry
from trip.models import trip_summary

#----------------------------------
# Index
#----------------------------------
def index(request):
    if request.user.is_authenticated:
        title = _('applications').capitalize()
        hide_title = False
    else:
        title = get_current_site(request)
        hide_title = True

    context = get_base_context(request, 0, 0, title)
    context['hide_title'] = hide_title
    context['trip_summary'] = trip_summary(request.user.id)
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
# Files List
#----------------------------------
def file_list(request, up):
    data = File.objects.filter(user = request.user.id, node = up).order_by('code', 'name')

    title_icon = ''
    title = _('files').capitalize()
    if (up != 0):
        file = get_object_or_404(File.objects.filter(id = up, user = request.user.id))
        if (file.app != ''):
            check = file.app + ':index'
            try:
                url = reverse(check)
                return HttpResponseRedirect(url)
            except:
                pass
        title_icon = file.icon
        title = file.name
        if (file.content != 0) and (file.ext == 'entry'):
            return HttpResponseRedirect(reverse('store:entry_form', args=(file.content,)))

    extra = { 'title_icon': title_icon }
    return show_page_list(request, up, title, 'file', data, extra)

#----------------------------------
def file_add(request, up):
    if (request.method == 'POST'):
        form = FileForm(request.POST)
    else:
        form = FileForm()
    return show_page_form(request, up, 0, _('file').capitalize(), 'file', form)

#----------------------------------
def file_form(request, pk):
    data = get_object_or_404(File.objects.filter(id = pk, user = request.user.id))
    if (request.method == 'POST'):
        form = FileForm(request.POST, instance = data)
    else:
        form = FileForm(instance = data)
    extra_context = {'qty': data.qty,}
    return show_page_form(request, data.node, pk, _('file').capitalize(), 'file', form, extra_context)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def file_del(request, pk):
    data = get_object_or_404(File.objects.filter(id = pk, user = request.user.id))
    node_id = data.node
    File.objects.get(id = pk).delete()
    dec_qty(request.user.id, node_id)
    return HttpResponseRedirect(reverse('file_list', args=(node_id,)))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def file_imp(request, up):
    data = get_object_or_404(File.objects.filter(id = up, user = request.user.id))
    if (data.storage == i_storage_type['entry']):
        rmtree(request.user, up)
        for grp in Group.objects.filter(user = request.user.id):
            pg = File.objects.create(
                    user = request.user, 
                    node = up, 
                    code = grp.code,
                    name = grp.name,
                    creation = grp.creation,
                    last_mod = grp.last_mod,
                    storage = i_storage_type['entry'])
            npp = 0
            for entry in Entry.objects.filter(user = request.user.id, group = grp.id, actual = 1).order_by('title'):
                File.objects.create(
                    user = request.user, 
                    node = pg.id, 
                    code = '%02d' % npp,
                    name = entry.title,
                    creation = entry.creation,
                    last_mod = entry.last_mod,
                    notes = entry.notes,
                    ext = 'entry',
                    content = entry.id)
                npp = npp + 1
            pg.qty = npp
            pg.save()
    return HttpResponseRedirect(reverse('file_list', args=(up,)))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
# Check hierarhy health
#----------------------------------
def health(request):
    check_health(request.user.id, 0)
    return HttpResponseRedirect(reverse('index'))



#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def show_page_list(request, node_id, title, name, data, extra_context = {}):
    context = get_base_context(request, node_id, 0, title)
    context[name + 's'] = data
    context.update(extra_context)
    template = loader.get_template(name + '_list.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def show_page_form(request, node_id, pk, title, name, form, extra_context = {}):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.user = request.user
            data.node = node_id
            last_mod = datetime.now()
            if (pk == 0):
                creation = datetime.now()
                inc_qty(request.user.id, node_id)
            form.save()
            pk = data.id
            return HttpResponseRedirect(reverse(name + '_list', args=(pk,)))
    context = get_base_context(request, node_id, pk, title)
    context['form'] = form
    context.update(extra_context)
    template = loader.get_template(name + '_form.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
# Toggle tree node
#----------------------------------
def toggle(request, pk):
    node = File.objects.filter(id = pk).get()
    node.is_open = not node.is_open
    node.save()
    return index(request)

#----------------------------------
# Feedback
#----------------------------------
def feedback(request):
    context = get_base_context(request, 0, 0, _('feedback').capitalize())
    template = loader.get_template('feedback.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
def inc_qty(user, pk):
    if (pk == 0):
        return
    data = get_object_or_404(File.objects.filter(id = pk, user = user))
    data.qty = data.qty + 1
    data.save()

#----------------------------------
def dec_qty(user, pk):
    if (pk == 0):
        return
    data = get_object_or_404(File.objects.filter(id = pk, user = user))
    data.qty = data.qty - 1
    data.save()

