from task.models import Task, TaskGroup, Urls
from task.base.views import BaseListView, BaseDetailView, BaseGroupView
from task.files import get_files_list
from task.categories import get_categories_list
from note.forms import CreateForm, EditForm
from note.config import app_config

class TuneData:
    def tune_dataset(self, data, view_mode):
        return data;

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, 'note', *args, **kwargs)

    def get_info(self, item):
        ret = []
        
        if (self.view_mode != 'by_group'):
            if TaskGroup.objects.filter(task=item.id, role=self.role).exists():
                ret.append({'text': TaskGroup.objects.filter(task=item.id, role=self.role).get().group.name})

        links = len(Urls.objects.filter(task=item.id)) > 0
    
        files = (len(get_files_list(item.user, self.app, self.role, item.id)) > 0)

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
        super().__init__(app_config, 'note', *args, **kwargs)

class GroupView(BaseGroupView, TuneData):
    def __init__(self, *args, **kwargs):
        super().__init__(app_config, 'note', *args, **kwargs)
