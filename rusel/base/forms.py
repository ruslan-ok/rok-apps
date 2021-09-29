from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from task.models import Group, Task, TaskGroup
from rusel.widgets import FileUpload

#----------------------------------
class BaseCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, config, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.role = role
        #self.fields['grp'].initial = self.get_group_id()
        #self.fields['grp'].queryset = Group.objects.filter(role=role).order_by('sort')
        
    def save(self, commit=True):
        ret = super().save(commit=False)
        ret.save()
        return ret

#----------------------------------
class BaseEditForm(forms.ModelForm):
    role = None

    upload = forms.FileField(
        label=_('attachments').capitalize(), 
        required=False, 
        widget=FileUpload())

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, config, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.role = role

    def clean_categories(self):
        self.cleaned_data['categories'] = ' '.join([self.data['categories_1'], self.data['categories_2']]).strip()
        return self.cleaned_data['categories']

    def get_group_id(self):
        task_id = self.instance.id
        tgs = TaskGroup.objects.filter(task=task_id)
        if (len(tgs) > 0):
            tg = tgs[0]
            grp = tg.group
            grp_id = grp.id
            return grp_id
        return None

