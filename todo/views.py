from datetime import datetime, date, timedelta
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils import formats
from task.const import APP_TODO, ROLE_TODO
from task.models import Task, Step
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
from rusel.utils import nice_date
from todo.forms import CreateForm, EditForm
from todo.config import app_config

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

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView, TuneData):
    model = Task
    form_class = CreateForm
    permission_required = 'task.view_todo'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView, TuneData):
    model = Task
    form_class = EditForm
    permission_required = 'task.change_todo'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ed_task = self.get_object()
        context['steps'] = Step.objects.filter(task = ed_task.id)
        context['del_step_text'] = _('Delete this step?')
        context['add_due_date_text'] = _('Add due date')
        context['termin_today_info'] = get_remind_today(3).strftime('%H:%M')
        context['termin_tomorrow_info'] = formats.date_format(get_remind_tomorrow(), 'D, H:i')
        context['termin_next_week_info'] = formats.date_format(get_remind_next_week(8), 'D, H:i')

        context['repeat_text'] = _('Repeat')
        context['repeat_form_d1'] = get_week_day_name(1)
        context['repeat_form_d2'] = get_week_day_name(2)
        context['repeat_form_d3'] = get_week_day_name(3)
        context['repeat_form_d4'] = get_week_day_name(4)
        context['repeat_form_d5'] = get_week_day_name(5)
        context['repeat_form_d6'] = get_week_day_name(6)
        context['repeat_form_d7'] = get_week_day_name(7)

        context['remind_text'] = _('To remind')
        context['remind_active'] = ed_task.remind and (not ed_task.completed) and (ed_task.remind > datetime.now())
        context['task_b_remind'] = (ed_task.remind != None)
        if ed_task.remind:
            context['task_remind_time'] = _('Remind in') + ' ' + ed_task.remind.strftime('%H:%M')
            context['task_remind_date'] = nice_date(ed_task.remind.date())
        context['remind_today_info'] = get_remind_today(2).strftime('%H:%M')
        context['remind_tomorrow_info'] = formats.date_format(get_remind_tomorrow(), 'D, H:i')
        context['remind_next_week_info'] = formats.date_format(get_remind_next_week(8), 'D, H:i')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if ('add_step' in form.changed_data):
            step = Step.objects.create(user = form.instance.user, name = self.request.POST['add_step'], task = form.instance)
        form.instance.get_info()
        return response


class GroupView(LoginRequiredMixin, BaseGroupView, TuneData):

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_week_day_name(weekday_num):
    d = date(2020, 7, 13)
    if (weekday_num > 1):
        d = d + timedelta(weekday_num - 1)
    return formats.date_format(d, 'D')

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

