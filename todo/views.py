from datetime import datetime, date, timedelta
from django.utils.translation import gettext_lazy as _
from task.const import APP_TODO, ROLE_TODO, NUM_ROLE_TODO
from task.models import Task, Step
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView, get_app_doc
from rusel.utils import nice_date
from todo.forms import CreateForm, EditForm
from todo.config import app_config
from todo.get_info import get_info

app = APP_TODO
role = ROLE_TODO

class TuneData:
    def tune_dataset(self, data, group):
        if (group.determinator == 'view'):
            if (group.view_id == 'myday'):
                return data.filter(in_my_day=True).exclude(completed=True)
            if (group.view_id == 'important'):
                return data.filter(important=True).exclude(completed=True)
            if (group.view_id == 'planned'):
                return data.exclude(stop=None).exclude(completed=True)
            if (group.view_id == 'completed'):
                return data.filter(completed=True)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ed_task = self.get_object()
        context['steps'] = Step.objects.filter(task = ed_task.id)
        context['del_step_text'] = _('delete this step?').capitalize()
        context['add_due_date_text'] = _('add due date').capitalize()
        context['termin_today_info'] = get_remind_today(3).strftime('%H:%M')
        context['termin_tomorrow_info'] = get_remind_tomorrow().strftime('%a, %H:%M')
        context['termin_next_week_info'] = get_remind_next_week(5).strftime('%a, %H:%M')

        context['repeat_text'] = _('repeat').capitalize()
        context['repeat_form_d1'] = get_week_day_name(1)
        context['repeat_form_d2'] = get_week_day_name(2)
        context['repeat_form_d3'] = get_week_day_name(3)
        context['repeat_form_d4'] = get_week_day_name(4)
        context['repeat_form_d5'] = get_week_day_name(5)
        context['repeat_form_d6'] = get_week_day_name(6)
        context['repeat_form_d7'] = get_week_day_name(7)

        context['remind_text'] = _('to remind').capitalize()
        context['remind_active'] = ed_task.remind and (not ed_task.completed) and (ed_task.remind > datetime.now())
        context['task_b_remind'] = (ed_task.remind != None)
        if ed_task.remind:
            context['task_remind_time'] = _('remind in').capitalize() + ' ' + ed_task.remind.strftime('%H:%M')
            context['task_remind_date'] = nice_date(ed_task.remind.date())
        context['remind_today_info'] = get_remind_today(2).strftime('%H:%M')
        context['remind_tomorrow_info'] = get_remind_tomorrow().strftime('%a, %H:%M')
        context['remind_next_week_info'] = get_remind_next_week(8).strftime('%a, %H:%M')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if ('add_step' in form.changed_data):
            step = Step.objects.create(user = form.instance.user, name = self.request.POST['add_step'], task = form.instance)
        form.instance.set_item_attr(app, get_info(form.instance))
        return response


class GroupView(BaseGroupView, TuneData):
    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)

def get_week_day_name(weekday_num):
    d = date(2020, 7, 13)
    if (weekday_num > 1):
        d = d + timedelta(weekday_num - 1)
    return d.strftime('%a')

def get_remind_today(hours):
    remind_today = datetime.now()
    remind_today += timedelta(hours=hours)
    if (remind_today.minute > 0):
        correct_min = -remind_today.minute
        if (remind_today.minute > 30):
            correct_min = 60 - remind_today.minute
        remind_today += timedelta(minutes=correct_min)
    return remind_today

def get_remind_tomorrow():
    return datetime.now().replace(hour=9, minute=0, second=0) + timedelta(1)

def get_remind_next_week(days):
    return datetime.now().replace(hour=9, minute=0, second=0) + timedelta(days - datetime.today().isoweekday())

