from datetime import datetime, date
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from task.models import Task
from core.views import BaseListView, BaseDetailView, BaseGroupView
from core.forms import GroupForm
from warr.forms import CreateForm, EditForm

role = 'warr'
app = 'warr'

class TuneData:
    def tune_dataset(self, data, group):
        if (group.determinator == 'view'):
            if (group.view_id == 'active'):
                return data.filter(stop__gt=datetime.today().date())
            if (group.view_id == 'expired'):
                return data.filter(stop__lt=datetime.today().date())
        return data

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView, TuneData):
    model = Task
    form_class = CreateForm
    permission_required = 'task.view_warranty'

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView, TuneData):
    model = Task
    form_class = EditForm
    permission_required = 'task.change_warranty'

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        item = form.instance
        item.stop = add_months(item.start, item.months)
        item.save()
        get_info(item)
        return response

def add_months(d, x):
    newmonth = ((( d.month - 1) + x ) % 12 ) + 1
    newyear  = int(d.year + ((( d.month - 1) + x ) / 12 ))
    newdate = date(newyear, newmonth, d.day)
    return newdate

class GroupView(LoginRequiredMixin, BaseGroupView, TuneData):
    form_class = GroupForm

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

def get_info(item):
    attr = [{'termin': True}]
    item.actualize_role_info(app, role, attr)
