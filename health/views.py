import pathlib

from datetime import datetime
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, HttpResponseNotFound
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q

from hier.models import get_app_params
from hier.aside import Fix
from hier.utils import get_base_context_ext, process_common_commands, sort_data, extract_get_params
from hier.params import get_search_mode, get_search_info, set_restriction, set_article_kind, set_article_visible
from hier.files import service_path
from .models import app_name, Biomarker, Incident, Anamnesis
from .forms import BiomarkerForm, IncidentForm
from .plot import Plot
from .secret import imp_file

items_in_page = 20

CHRONO = 'chrono'
BIOMARK = 'biomark'
INCIDENT = 'incident'

#----------------------------------
def chrono(request):
    set_restriction(request.user, app_name, CHRONO)
    return HttpResponseRedirect(reverse('health:main'))

#----------------------------------
def biomark(request):
    set_restriction(request.user, app_name, BIOMARK)
    return HttpResponseRedirect(reverse('health:main'))

#----------------------------------
def incident(request):
    set_restriction(request.user, app_name, INCIDENT)
    return HttpResponseRedirect(reverse('health:main'))

#----------------------------------
def item_form(request, pk):
    set_article_kind(request.user, app_name, 'item', pk)
    return HttpResponseRedirect(reverse('health:main') + extract_get_params(request))

#----------------------------------
def imp_weight(request):
    do_import_weight(request.user)
    return HttpResponseRedirect(reverse('health:main'))

#----------------------------------
def chart(request, nm):
    fsock = open(chart_storage(request.user) + nm + '.png', 'rb')
    return FileResponse(fsock)

#----------------------------------
@login_required(login_url='account:login')
def main(request):
    app_param = get_app_params(request.user, app_name)
    if (app_param.restriction != CHRONO) and (app_param.restriction != BIOMARK) and (app_param.restriction != INCIDENT):
        set_restriction(request.user, app_name, CHRONO)
        app_param = get_app_params(request.user, app_name)

    if process_common_commands(request, app_name): # aside open/close, article open/close
        return HttpResponseRedirect(reverse('health:main') + extract_get_params(request))

    app_param, context = get_base_context_ext(request, app_name, 'health', get_title(app_param.restriction))

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            item = None
            if (app_param.restriction == BIOMARK):
                item = create_biomarkers(request.user, request.POST['item_add-name'])
            if (app_param.restriction == INCIDENT):
                item = Incident.objects.create(user = request.user, name = request.POST['item_add-name'], beg = datetime.now(), end = datetime.now())
            if item:
                return HttpResponseRedirect(reverse('health:item_form', args = [item.id]))

    fixes = []
    fixes.append(Fix(CHRONO, _('chronology').capitalize(), 'rok/icon/all.png', 'chrono/', None))
    fixes.append(Fix(BIOMARK, _('biomarkers').capitalize(), 'rok/icon/all.png', 'biomark/', len(Biomarker.objects.filter(user = request.user.id))))
    fixes.append(Fix(INCIDENT, _('incidents').capitalize(), 'rok/icon/all.png', 'incident/', len(Incident.objects.filter(user = request.user.id))))
    context['fix_list'] = fixes
    context['without_lists'] = True
    context['add_item_placeholder'] = get_placeholder(app_param.restriction)
    context['hide_selector'] = True
    context['hide_important'] = True
    if (app_param.restriction == CHRONO):
        context['hide_add_item_input'] = True
        min_value, max_value, min_date, max_date, last_value = build_chart(request.user, 'weight', 73)
        context['weight_min_value'] = min_value
        context['weight_min_date'] = min_date
        context['weight_max_value'] = max_value
        context['weight_max_date'] = max_date
        context['weight_last_value'] = last_value
        min_value, max_value, min_date, max_date, last_value = build_chart(request.user, 'temp', 37)
        context['temp_min_value'] = min_value
        context['temp_min_date'] = min_date
        context['temp_max_value'] = max_value
        context['temp_max_date'] = max_date
        context['temp_last_value'] = last_value
        min_value, max_value, min_date, max_date, last_value = build_chart(request.user, 'waist', 90)
        context['waist_min_value'] = min_value
        context['waist_min_date'] = min_date
        context['waist_max_value'] = max_value
        context['waist_max_date'] = max_date
        context['waist_last_value'] = last_value

    redirect = False

    if app_param.article:
        valid_article = False
        if (app_param.restriction == BIOMARK):
            valid_article = Biomarker.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if (app_param.restriction == INCIDENT):
            valid_article = Incident.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if valid_article:
            if (app_param.restriction == BIOMARK):
                item = get_object_or_404(Biomarker.objects.filter(id = app_param.art_id, user = request.user.id))
                redirect = edit_item(request, context, app_param.restriction, item, False)
            if (app_param.restriction == INCIDENT):
                item = get_object_or_404(Incident.objects.filter(id = app_param.art_id, user = request.user.id))
                disable_delete = Anamnesis.objects.filter(incident = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, item, disable_delete)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('health:main') + extract_get_params(request))

    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    data = filtered_sorted_list(request.user, app_param, query)

    page_number = 1
    if (request.method == 'GET'):
        page_number = request.GET.get('page')
    paginator = Paginator(data, items_in_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)
    context['search_info'] = get_search_info(query)
    context['search_qty'] = len(data)
    context['search_data'] = query and (len(data) > 0)
    template = loader.get_template('health/' + app_param.restriction + '.html')
    return HttpResponse(template.render(context, request))


#----------------------------------
def filtered_sorted_list(user, app_param, query):
    data = filtered_list(user, app_param.restriction, query, app_param.lst)
    return data

#----------------------------------
def filtered_list(user, restriction, query = None, lst = None):
    if (restriction == BIOMARK):
        data = Biomarker.objects.filter(user = user.id).order_by('-publ')
    elif (restriction == INCIDENT):
        data = Incident.objects.filter(user = user.id).order_by('-beg')
    else:
        data = []
    return data
#----------------------------------
def get_title(restriction):
    if (restriction == CHRONO):
        return _('dynamics of changes in biomarkers').capitalize()
    if (restriction == BIOMARK):
        return _('biomarkers').capitalize()
    if (restriction == INCIDENT):
        return _('incidents').capitalize()

#----------------------------------
def get_placeholder(restriction):
    if (restriction == BIOMARK):
        return _('add biomarkers').capitalize()
    if (restriction == INCIDENT):
        return _('add incident').capitalize()
    return None

#----------------------------------
def edit_item(request, context, restriction, item, disable_delete = False):
    form = None
    if (request.method == 'POST'):
        if ('item_delete' in request.POST):
            delete_item(request, item, disable_delete)
            return True
        if ('item_save' in request.POST):
            if (restriction == BIOMARK):
                form = BiomarkerForm(request.POST, instance = item)
            elif (restriction == INCIDENT):
                form = IncidentForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                form.save()
                return True

    if not form:
        if (restriction == BIOMARK):
            form = BiomarkerForm(instance = item)
        elif (restriction == INCIDENT):
            form = IncidentForm(instance = item)

    context['form'] = form
    context['ed_item'] = item
    return False

#----------------------------------
def delete_item(request, item, disable_delete = False):
    if disable_delete:
        return False
    item.delete()
    set_article_visible(request.user, app_name, False)
    return True

#----------------------------------
def create_biomarkers(user, s_value):
    height = None
    weight = None
    temp = None
    waist = None
    systolic = None
    diastolic = None
    pulse = None
    info = ''
    n_value = 0

    try:
        n_value = float(s_value.replace(',', '.'))
    except ValueError:
        info = s_value

    if (n_value >= 35) and (n_value < 50):
        temp = n_value
    elif (n_value >= 50) and (n_value < 90):
        weight = n_value
    elif (n_value >= 90) and (n_value < 150):
        waist = n_value
    elif (n_value >= 150) and (n_value < 250):
        height = n_value
    
    return Biomarker.objects.create(user = user, height = height, weight = weight, temp = temp, waist = waist, \
                                    systolic = systolic, diastolic = diastolic, pulse = pulse, info = info, publ = datetime.now())

#----------------------------------
def get_data_from_db(user, name):
    x = []
    y = []
    min_value = max_value = min_date = max_date = last_value = None

    if (name == 'weight'):
        data = Biomarker.objects.filter(user = user.id).exclude(weight = None).order_by('publ')
        if (len(data) > 0):
            values = Biomarker.objects.filter(user = user.id).exclude(weight = None).order_by('weight')
            min_value = values[0].weight
            max_value = values[len(values)-1].weight
            min_date = values[0].publ.date()
            max_date = values[len(values)-1].publ.date()
            last_value = data[len(data)-1].weight
    elif (name == 'waist'):
        data = Biomarker.objects.filter(user = user.id).exclude(waist = None).order_by('publ')
        if (len(data) > 0):
            values = Biomarker.objects.filter(user = user.id).exclude(waist = None).order_by('waist')
            min_value = values[0].waist
            max_value = values[len(values)-1].waist
            min_date = values[0].publ.date()
            max_date = values[len(values)-1].publ.date()
            last_value = data[len(data)-1].waist
    elif (name == 'temp'):
        data = Biomarker.objects.filter(user = user.id).exclude(temp = None).order_by('publ')
        if (len(data) > 0):
            values = Biomarker.objects.filter(user = user.id).exclude(temp = None).order_by('temp')
            min_value = values[0].temp
            max_value = values[len(values)-1].temp
            min_date = values[0].publ.date()
            max_date = values[len(values)-1].publ.date()
            last_value = data[len(data)-1].temp
    else:
        data = []
    
    cur_day = average = qty = None
    for b in data:
        if cur_day and (cur_day == b.publ.date()):
            qty += 1
            if (name == 'weight'):
                average += b.weight
            elif (name == 'waist'):
                average += b.waist
            elif (name == 'temp'):
                average += b.temp
        else:
            if cur_day:
                x.append(cur_day)
                if (cur_day == min_date):
                    y.append(min_value)
                elif (cur_day == max_date):
                    y.append(max_value)
                else:
                    y.append(average / qty)
            qty = 1
            cur_day = b.publ.date()
            if (name == 'weight'):
                average = b.weight
            elif (name == 'waist'):
                average = b.waist
            elif (name == 'temp'):
                average = b.temp
    
    return x, y, min_value, max_value, min_date, max_date, last_value

#----------------------------------
def check_l(x, i, approx):
    """Проверка сплайна слева"""
    qty_l = 0
    j = i - 1
    while (j >= 0) and ((x[i] - x[j]).days <= approx):
        qty_l += 1
        j -= 1
    return qty_l

#----------------------------------
def check_r(x, i, approx):
    """Проверка сплайна справа"""
    qty_r = 0
    j = i + 1
    while (j < len(x)) and ((x[j] - x[i]).days <= approx):
        qty_r += 1
        j += 1
    return qty_r

#----------------------------------
def approximate(x, y, approx):
    """Аппроксимация значений на графике"""
    ret_y = []
    prev_x = prev_y = 0
    for i in range(len(y)):
        # определяем сплайны слева и справа
        qty_l = check_l(x, i, approx)
        qty_r = check_r(x, i, approx)
        # и усредняем значения для них
        average = 0
        for j in range(i - qty_l, i + qty_r + 1):
            average += y[j]
        average /= (1 + qty_l + qty_r)
        ret_y.append(average)
    return ret_y

#----------------------------------
def build_chart(user, name, border):
    x, y, min_value, max_value, min_date, max_date, last_vaue = get_data_from_db(user, name)

    if (name == 'waist'):
        min_value = 90

    min_date = max_date = None
    if x:
        min_date = x[0]
        max_date = x[-1]

    if (len(y) > 100):
        y = approximate(x, y, 10)
 
    plt = Plot(chart_storage(user), name, min_value, max_value, min_date, max_date)

    prev_value = prev_date = high = None
    xx = []
    yy = []
    for i in range(len(y)):
        if not prev_value:
            prev_value = y[i]
            prev_date = x[i]
            high = (y[i] >= border)
            xx.append(x[i])
            yy.append(y[i])
        else:
            if (high == (y[i] >= border)):
                xx.append(x[i])
                yy.append(y[i])
            else:
                if high:
                    color = 'brown'
                else:
                    color = 'green'
                if (len(y) > 300):
                    plt.plot(xx, yy, color = color)
                else:
                    plt.scatter(xx, yy, color = color)
                xx = []
                yy = []
                xx.append(x[i])
                yy.append(y[i])
                high = (y[i] >= border)
    if high:
        color = 'brown'
    else:
        color = 'green'
    if (len(y) > 300):
        plt.plot(xx, yy, color = color)
    else:
        plt.scatter(xx, yy, color = color)
    bx = [min_date, max_date]
    by = [border, border]
    plt.plot(bx, by, linestyle = 'dotted', color = 'navy')
    plt.save()
    return min_value, max_value, min_date, max_date, last_vaue

#----------------------------------
def chart_storage(user):
    path = service_path.format(user.id) + app_name + '/'
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    return path

#----------------------------------
def do_import_weight(user):
    with open(imp_file, 'r') as f:
        while True:
            s = f.readline()
            if (s == ''):
                break
            ss = s.split(',')
            dt = datetime.fromtimestamp(int(ss[0]))
            vl = float(ss[1].replace('\n', ''))
            Biomarker.objects.create(user = user, publ = dt, weight = vl, info = 'Imported from http://mifit.huami.com/t/account_mifit')

