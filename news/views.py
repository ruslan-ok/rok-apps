from task.models import Task, TaskGroup, Urls
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
from task.files import get_files_list
from task.categories import get_categories_list
from news.forms import CreateForm, EditForm
from news.config import app_config

role = 'news'

class TuneData:
    def tune_dataset(self, data, view_mode):
        return data;

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

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
                ret.append({'icon': 'newspaper'})
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

class GroupView(BaseGroupView, TuneData):
    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
