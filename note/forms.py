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
    grp = forms.ModelChoiceField(
        label=_('group').capitalize(),
        queryset=Group.objects.filter(role=ROLE_NOTE).order_by('sort'), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control mb-5'}))

    class Meta:
        model = Task
        fields = ['name', 'stop', 'info', 'grp']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-5'}),
            'stop': AdminDateWidget(attrs={'class': 'form-control mb-5'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-5'}),
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