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
            self.fields['grp'].queryset = Group.objects.filter(user=self.instance.user.id, role=role, determinator=None).order_by('sort')

    def clean_categories(self):
        self.cleaned_data['categories'] = ' '.join([self.data['categories_1'], self.data['categories_2']]).strip()
        return self.cleaned_data['categories']

    def get_group_id(self):
        task_id = self.instance.id
        tgs = TaskGroup.objects.filter(task=task_id)
        if (len(tgs) > 0):
            tg = tgs[0]
            grp = tg.group
            return grp.id
        return None

#----------------------------------
class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

#----------------------------------
class GroupForm(forms.ModelForm):
    node = forms.ChoiceField(
        label=_('node').capitalize(),
        widget=forms.Select(attrs={'class': 'form-control mb-2'}),
        choices=[(0, '------'),]
    )
    completed = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('display completed records').capitalize()}))
    class Meta:
        model = Group
        fields = ['name', 'sort', 'node', 'completed']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-2', 'id': 'id_grp_name'}),
            'node': forms.Select(attrs={'class': 'form-control mb-2'}),
            'sort': forms.TextInput(attrs={'class': 'form-control mb-2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ('node' in self.fields):
            self.fields['node'].choices = self.get_node_hier(self.instance)

    def get_node_hier(self, group):
        groups = [(0, '----------'),]
        self.get_sorted_groups(groups, group.user.id, group.role, group.id)
        return groups

    def get_sorted_groups(self, groups, user_id, role, curr_id, node=None, level=0):
        node_id = None
        if node:
            node_id = node.id
        items = Group.objects.filter(user=user_id, role=role, node=node_id).order_by('sort')
        for item in items:
            if (item.id != curr_id) and (item.determinator != 'role') and (item.determinator != 'view'):
                groups.append((item.id, level * '—' + '  ' + item.name),)
                self.get_sorted_groups(groups, user_id, role, curr_id, item, level+1)

    def clean_node(self):
        ret = None
        node_ok = self.cleaned_data['node']
        if node_ok:
            inst_id = self.instance.id
            node_id = node_ok
            test = Group.objects.filter(id=node_id).get()
            ret = test
            if (test.id == inst_id):
                raise  ValidationError(_('self reference').capitalize())
            
            while test.node:
                node_id = test.node.id
                test = Group.objects.filter(id=node_id).get()
                if (test.id == inst_id):
                    raise  ValidationError(_('loop link').capitalize())

            gts = TaskGroup.objects.filter(group=node_ok)
            if (len(gts) > 0):
                raise  ValidationError(_('not empty node group').capitalize())

        return ret

