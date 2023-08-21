from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from cram.models import CramGroup, Phrase

class GroupForm(forms.ModelForm):
    name = forms.CharField(
        label=_('Group name'),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mb-2'}),)
    sort = forms.CharField(
        label=_('Sort code'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-2'}),)
    node = forms.ChoiceField(
        label=_('Node'),
        widget=forms.Select(attrs={'class': 'form-control mb-2'}),
        choices=[(0, '------'),])
    currency = forms.CharField(
        label=_('Languages'),
        widget=forms.TextInput(attrs={'class': 'form-control mb-2'}))

    class Meta:
        model = CramGroup
        fields = ['name', 'sort', 'node', 'currency']

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
        items = CramGroup.objects.filter(user=user_id, role=role, node=node_id).order_by('sort')
        for item in items:
            if (item.id != curr_id) and (item.determinator != 'role') and (item.determinator != 'view'):
                groups.append((item.id, level * '—' + '  ' + item.name),)
                self.get_sorted_groups(groups, user_id, role, curr_id, item, level+1)

    def clean_node(self):
        ret = None
        node_ok = int(self.cleaned_data['node'])
        if node_ok:
            inst_id = self.instance.id
            node_id = node_ok
            test = CramGroup.objects.filter(id=node_id).get()
            ret = test
            if (test.id == inst_id):
                raise  ValidationError(_('Self reference'))
            
            while test.node:
                node_id = test.node.id
                test = CramGroup.objects.filter(id=node_id).get()
                if (test.id == inst_id):
                    raise  ValidationError(_('Loop link'))

            gts = Phrase.objects.filter(group=node_ok)
            if (len(gts) > 0):
                raise  ValidationError(_('Not empty node group'))

        return ret

