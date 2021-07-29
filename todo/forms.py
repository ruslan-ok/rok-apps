from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.contrib.admin.widgets import AdminSplitDateTime

from task.models import Group, Task, TaskGroup
from todo.models import app_name, Step

class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name']
        
class TaskForm(forms.ModelForm):
    add_step = forms.CharField(widget = forms.TextInput(attrs = {'placeholder': _('next step').capitalize(), 'onchange': 'stepAdd()'}), required = False)
    remind = forms.SplitDateTimeField(widget = AdminSplitDateTime(attrs = {'onchange': 'afterCalendarChanged(0,1)'}), label = _('remind').capitalize(), required = False)
    stop = forms.SplitDateTimeField(widget = AdminSplitDateTime(attrs = {'onchange': 'afterCalendarChanged(0,2)'}), label = _('termin').capitalize(), required = False)
    url = forms.CharField(widget = forms.TextInput(attrs = {'placeholder': _('add link').capitalize()}), required = False)
    category = forms.CharField(widget = forms.TextInput(attrs = {'placeholder': _('add category').capitalize()}), required = False)
    lst = forms.ChoiceField(choices=[])
    cur_group = 0

    class Meta:
        model = Task
        fields = ['name', 'add_step', 'stop', 'remind', 'repeat', 'repeat_num', 'repeat_days', 'info', 'url', 'category', 'lst']
                  #'app_task', 'app_note', 'app_news', 'app_store', 'app_doc', 'app_warr', 'app_expen',
                  #'app_trip', 'app_fuel', 'app_apart', 'app_health', 'app_work', 'app_photo', 'lst']
        widgets = {'info': forms.Textarea(attrs={'rows':3, 'cols':10, 'placeholder': _('add note').capitalize(), 'data-autoresize':''}),}

    def __init__(self, * args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        instance = kwargs.pop('instance')
        self.fields['lst'].choices = Group.get_tree(instance.user.id, 'todo')
        if TaskGroup.objects.filter(task=instance.id, app='todo').exists():
            self.cur_group = TaskGroup.objects.filter(task=instance.id, app='todo').get().group.id
            self.initial['lst'] = self.cur_group
            pass

    def _save_m2m(self):
        super()._save_m2m()
        new_group = int(self.cleaned_data['lst'])
        if (new_group != self.cur_group):
            if (new_group == 0):
                # delete
                TaskGroup.objects.filter(task=self.instance.id, group=self.cur_group, app='todo').get().delete()
            else:
                group = Group.objects.filter(id=new_group).get()
                if (self.cur_group == 0):
                    # insert
                    tg = TaskGroup.objects.create(task=self.instance, group=group, app='todo')
                else:
                    # update
                    tg = TaskGroup.objects.filter(task=self.instance.id, group=self.cur_group, app='todo').get()
                    tg.group = group
                    tg.save()
            self.cur_group = new_group

