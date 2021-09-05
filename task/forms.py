from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from task.models import Group

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['node', 'name', 'sort']
        widgets = {
            'node': forms.Select(attrs={'class': 'form-control mb-5'}),
            'name': forms.TextInput(attrs={'class': 'form-control mb-5'}),
            'sort': forms.TextInput(attrs={'class': 'form-control mb-5'}),
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

