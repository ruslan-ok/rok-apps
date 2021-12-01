from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from task.models import Group, Task, TaskGroup
from rusel.widgets import FileUpload, SwitchInput

#----------------------------------
class BaseCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, config, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.role = role
        #self.fields['grp'].initial = get_cur_grp(self.request)
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
        if ('grp' in self.fields):
            self.fields['grp'].initial = self.get_group_id()
            self.fields['grp'].queryset = Group.objects.filter(role=role).order_by('sort')

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

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class GroupForm(forms.ModelForm):
    hier = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('display records as a hierarchy').capitalize()}))
    completed = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('display completed records').capitalize()}))
    class Meta:
        model = Group
        fields = ['node', 'name', 'color', 'sort', 'wallpaper', 'hier', 'completed']
        widgets = {
            'node': forms.Select(attrs={'class': 'form-control mb-2'}),
            'name': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            'sort': forms.TextInput(attrs={'class': 'mb-2'}),
            'wallpaper': forms.ClearableFileInput(),
            'color': forms.TextInput(attrs={'class': 'form-control-sm mb-2', 'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['node'].queryset = Group.objects.filter(user=self.instance.user.id, role=self.instance.role).order_by('sort')

    def clean_node(self):
        node_ok = self.cleaned_data['node']
        if node_ok:
            inst_id = self.instance.id
            node_id = node_ok.id
            test = Group.objects.filter(id = node_id).get()
            if (test.id == inst_id):
                raise  ValidationError(_('self reference'))
            
            while test.node:
                node_id = test.node.id
                test = Group.objects.filter(id = node_id).get()
                if (test.id == inst_id):
                    raise  ValidationError(_('loop link'))

        return node_ok

