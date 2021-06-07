from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.contrib.admin.widgets import AdminSplitDateTime

from hier.forms import DateInput
from task.models import Group, Task
from todo.models import app_name, Step

class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name']
        
class TaskForm(forms.ModelForm):
    add_step = forms.CharField(widget = forms.TextInput(attrs = {'placeholder': _('next step').capitalize()}), required = False)
    remind = forms.SplitDateTimeField(widget = AdminSplitDateTime(attrs = {'onchange': 'afterCalendarChanged(0,1)'}), label = _('remind').capitalize(), required = False)
    stop = forms.SplitDateTimeField(widget = AdminSplitDateTime(attrs = {'onchange': 'afterCalendarChanged(0,2)'}), label = _('termin').capitalize(), required = False)
    url = forms.CharField(widget = forms.TextInput(attrs = {'placeholder': _('add link').capitalize()}), required = False)
    category = forms.CharField(widget = forms.TextInput(attrs = {'placeholder': _('add category').capitalize()}), required = False)

    class Meta:
        model = Task
        fields = ['name', 'add_step', 'stop', 'remind', 'repeat', 'repeat_num', 'repeat_days', 'info', 'url', 'category']
        widgets = {'info': forms.Textarea(attrs={'rows':3, 'cols':10, 'placeholder': _('add note').capitalize(), 'data-autoresize':''}),}

