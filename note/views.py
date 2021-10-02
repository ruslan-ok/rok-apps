from task.const import ROLE_NOTE, NUM_ROLE_NOTE
from task.models import Task, TaskGroup, Urls
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView, get_app_doc
from rusel.files import get_files_list
from rusel.categories import get_categories_list
from note.forms import CreateForm, EditForm
from note.config import app_config
from note.get_info import get_info

app = 'note'
role = ROLE_NOTE

class TuneData:
    def tune_dataset(self, data, view_mode):
        return data;

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_note = NUM_ROLE_NOTE
        response = super().form_valid(form)
        return response

    def get_info(self, item):
        ret = []
        
        if (self.config.cur_view != 'by_group'):
            if TaskGroup.objects.filter(task=item.id, role=self.config.role).exists():
                ret.append({'text': TaskGroup.objects.filter(task=item.id, role=self.config.role).get().group.name})

        links = len(Urls.objects.filter(task=item.id)) > 0
    
        files = (len(get_files_list(item.user, self.config.app, self.config.role, item.id)) > 0)

        if item.info or links or files:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            if item.info:
                ret.append({'icon': 'notes'})
            if links:
                ret.append({'icon': 'url'})
            if files:
                ret.append({'icon': 'attach'})
    
        if item.categories:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            categs = get_categories_list(item.categories)
            for categ in categs:
                ret.append({'icon': 'category', 'text': categ.name, 'color': 'category-design-' + categ.design})
    
        return ret

class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.set_item_attr(app, get_info(form.instance))
        return response


class GroupView(BaseGroupView, TuneData):
    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)

