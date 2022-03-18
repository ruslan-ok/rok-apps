from datetime import datetime, date
from task.const import ROLE_WARR, ROLE_APP
from task.models import Task, Urls, TaskGroup
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
from rusel.base.forms import GroupForm
from rusel.categories import get_categories_list
from rusel.app_doc import get_app_doc
from warr.forms import CreateForm, EditForm
from warr.config import app_config

role = ROLE_WARR
app = ROLE_APP[role]

class TuneData:
    def tune_dataset(self, data, group):
        if (group.determinator == 'view'):
            if (group.view_id == 'active'):
                return data.filter(stop__gt=datetime.today())
            if (group.view_id == 'expired'):
                return data.filter(stop__lt=datetime.today())
        return data

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        item = form.instance
        item.stop = add_months(item.start, item.months)
        item.save()
        attr = get_info(item)
        item.set_item_attr(app, attr)
        return response

def add_months(d, x):
    newmonth = ((( d.month - 1) + x ) % 12 ) + 1
    newyear  = int(d.year + ((( d.month - 1) + x ) / 12 ))
    newdate = date(newyear, newmonth, d.day)
    return newdate

class GroupView(BaseGroupView, TuneData):
    form_class = GroupForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_info(item):
    attr = []

    links = len(Urls.objects.filter(task=item.id)) > 0
    files = (len(item.get_files_list(app, role)) > 0)

    if item.info or links or files:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        if links:
            attr.append({'icon': 'url'})
        if files:
            attr.append({'icon': 'attach'})
        if item.info:
            info_descr = item.info[:80]
            if len(item.info) > 80:
                info_descr += '...'
            attr.append({'icon': 'notes', 'text': info_descr})

    if item.categories:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        categs = get_categories_list(item.categories)
        for categ in categs:
            attr.append({'icon': 'category', 'text': categ.name, 'color': 'category-design-' + categ.design})
    
    ret = {'attr': attr}

    ret['attr'].append({'termin': True})

    if TaskGroup.objects.filter(task=item.id, role=role).exists():
        ret['group'] = TaskGroup.objects.filter(task=item.id, role=role).get().group.name

    return ret

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
