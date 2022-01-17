from django.utils.translation import gettext_lazy as _
from rusel.base.views import BaseListView, BaseDetailView
from health.forms.incident import CreateForm, EditForm
from task.const import ROLE_INCIDENT, ROLE_APP
from task.models import Task, Urls
from health.config import app_config
from rusel.files import get_files_list, get_app_doc
from rusel.categories import get_categories_list

role = ROLE_INCIDENT
app = ROLE_APP[role]

class TuneData:
    def tune_dataset(self, data, group):
        return data;

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
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

def get_info(item):
    attr = []

    if item.start:
        attr.append({'text': '{} {}'.format(_('from'), item.start.strftime('%d.%m.%Y'))})

    if item.stop:
        attr.append({'text': '{} {}'.format(_('to'), item.stop.strftime('%d.%m.%Y'))})

    if item.diagnosis:
        attr.append({'text': item.diagnosis})

    links = len(Urls.objects.filter(task=item.id)) > 0
    files = (len(get_files_list(item.user, app, role, item.id)) > 0)

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
    return ret

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)

