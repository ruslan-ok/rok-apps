from task.const import ROLE_EXPENSE, ROLE_APP
from task.models import Task, Urls, TaskGroup
from rusel.app_doc import get_app_doc
from rusel.categories import get_categories_list
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
from expen.forms import CreateForm, EditForm, ProjectForm
from expen.config import app_config

role = ROLE_EXPENSE
app = ROLE_APP[role]

class TuneData:
    def tune_dataset(self, data, group):
        return data

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if (not self.config.cur_view_group.determinator):
            if ('group_path' in context):
                context['summary'] = self.config.cur_view_group.expen_summary()
        return context


class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = context['title'] 
        if not title and self.object.expen_kontr:
            title = self.object.expen_kontr
        if not title and self.object.info:
            title = self.object.info.split('\n')[0]
        if not title and self.object.expen_qty and self.object.expen_price:
            title = str(self.object.expen_qty*self.object.expen_price)
        if not title:
            title = self.object.event.strftime('%d %b %Y')

        context['title'] = title
        grp = self.get_group()
        if grp:
            context['expen_byn'] = grp.expen_byn
            context['expen_usd'] = grp.expen_usd
            context['expen_eur'] = grp.expen_eur
        context['summary'] = self.object.expen_summary()
        context['amount_nc'] = currency_repr(self.object.expen_amount('BYN'))
        return context

    def get_group(self):
        tgs = TaskGroup.objects.filter(task=self.object.id)
        if (len(tgs) > 0):
            return tgs[0].group
        return None

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

def currency_repr(value):
    if (round(value, 2) % 1):
        return '{:,.2f}'.format(value).replace(',', '`')
    return '{:,.0f}'.format(value).replace(',', '`')

def get_info(item):
    attr = []
    attr.append({'text': ', '.join(item.expen_summary())})

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

    if TaskGroup.objects.filter(task=item.id, role=role).exists():
        ret['group'] = TaskGroup.objects.filter(task=item.id, role=role).get().group.name

    return ret


class ProjectView(BaseGroupView, TuneData):
    form_class = ProjectForm
    template_name = 'expen/project.html'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)

