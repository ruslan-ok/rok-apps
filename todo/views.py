from datetime import date, datetime
from django.utils.translation import gettext_lazy as _
from task.const import ROLE_TODO, NUM_ROLE_TODO
from task.models import Task, TaskGroup, Urls, Step
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView, get_app_doc
from rusel.files import get_files_list
from rusel.categories import get_categories_list
from todo.forms import CreateForm, EditForm
from todo.config import app_config

role = ROLE_TODO

class TuneData:
    def tune_dataset(self, data, view_mode):
        if (view_mode == 'todo'):
            return data.filter(in_my_day=True).exclude(completed=True)
        if (view_mode == 'important'):
            return data.filter(important=True).exclude(completed=True)
        if (view_mode == 'planned'):
            return data.exclude(stop=None).exclude(completed=True)
        if (view_mode == 'completed'):
            return data.filter(completed=True)
        return data;

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_task = NUM_ROLE_TODO
        response = super().form_valid(form)
        return response

    def get_info(self, item):
        ret = []
        
        if (self.config.cur_view != 'by_group'):
            if TaskGroup.objects.filter(task=item.id, role=self.config.role).exists():
                ret.append({'text': TaskGroup.objects.filter(task=item.id, role=self.config.role).get().group.name})

        if item.in_my_day and (self.config.cur_view != 'todo'):
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            ret.append({'icon': 'myday', 'color': 'black', 'text': _('My day')})

        step_total = 0
        step_completed = 0
        for step in Step.objects.filter(task=item.id):
            step_total += 1
            if step.completed:
                step_completed += 1
        if (step_total > 0):
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            ret.append({'text': '{} {} {}'.format(step_completed, _('out of'), step_total)})

        d = item.stop
        if d:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            s = item.termin_date()
            repeat = 'repeat'
            if item.b_expired():
                if item.completed:
                    icon = 'termin'
                    color = ''
                else:
                    icon = 'termin-expired'
                    color = 'expired'
                    repeat = 'repeat-expired'
                ret.append({'icon': icon, 'color': color, 'text': s})
            elif (item.stop == date.today()):
                if item.completed:
                    icon = 'termin'
                    color = ''
                else:
                    icon = 'termin-actual'
                    color = 'actual'
                    repeat = 'repeat-actual'
                ret.append({'icon': icon, 'color': color, 'text': s})
            else:
                ret.append({'icon': 'termin', 'text': s})
    
            if (item.repeat != 0):
                ret.append({'icon': repeat})
    
        links = len(Urls.objects.filter(task=item.id)) > 0
    
        files = (len(get_files_list(item.user, self.config.app, self.config.role, item.id)) > 0)

        if ((item.remind != None) and (item.remind >= datetime.now())) or item.info or links or files:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            if ((item.remind != None) and (item.remind >= datetime.now())):
                ret.append({'icon': 'remind'})
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
        
        if item.completed:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            ret.append({'text': '{}: {}'.format(_('completion').capitalize(), item.completion.strftime('%d.%m.%Y'))})

        return ret

class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

class GroupView(BaseGroupView, TuneData):
    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
