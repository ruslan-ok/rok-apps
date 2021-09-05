from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import AdminSplitDateTime, AdminDateWidget

from task.models import Group, Task, TaskGroup
from note.const import app_name
from task.const import ROLE_NOTE

#----------------------------------
class CreateNoteForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name']
        
#----------------------------------
class NoteForm(forms.ModelForm):
    stop = forms.DateTimeField(
        label=_('publication date').capitalize(),
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime mb-3', 'type': 'datetime-local'}))
    info = forms.CharField(
        label=_('description').capitalize(),
        widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}))
    grp = forms.ModelChoiceField(
        label=_('group').capitalize(),
        queryset=Group.objects.filter(role=ROLE_NOTE).order_by('sort'), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select mb-3'}))
    url = forms.CharField(
        label=_('add').capitalize() + ' URL',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    category = forms.CharField(
        label=_('add category').capitalize(),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))

    class Meta:
        model = Task
        fields = ['name', 'stop', 'info', 'grp', 'url', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'stop': AdminDateWidget(attrs={'class': 'form-control mb-3'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grp'].initial = self.get_group_id()

    def get_group_id(self):
        task_id = self.instance.id
        tgs = TaskGroup.objects.filter(task=task_id)
        if (len(tgs) > 0):
            tg = tgs[0]
            grp = tg.group
            grp_id = grp.id
            return grp_id
        return None

# Task.objects.filter(groups__app__startswith='todo')