from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import AdminSplitDateTime, AdminDateWidget

from task.models import Group, Task, TaskGroup
from todo.const import app_name
from task.const import ROLE_TODO
from task.widgets import UrlsInput, CategoriesInput, FileUpload

#----------------------------------
class CreateTodoForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name']
        
#----------------------------------
class TodoForm(forms.ModelForm):
    add_step = forms.CharField(widget = forms.TextInput(attrs = {'placeholder': _('next step').capitalize()}), required = False)
    stop = forms.DateTimeField(
        label=_('publication date').capitalize(),
        required=False,
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime mb-3', 'type': 'datetime-local'}))
    info = forms.CharField(
        label=_('description').capitalize(),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}))
    grp = forms.ModelChoiceField(
        label=_('group').capitalize(),
        queryset=Group.objects.filter(role=ROLE_TODO).order_by('sort'), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select mb-3'}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add link').capitalize()}))
    categories = forms.CharField(
        label=_('categories').capitalize(),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add category').capitalize()}))
    upload = forms.FileField(
        label=_('attachments').capitalize(), 
        required=False, 
        widget=FileUpload())

    class Meta:
        model = Task
        fields = ['completed', 'name', 'important', 'add_step', 'in_my_day', 'remind', 'stop', 'repeat', 'repeat_num', 'repeat_days', 
                'categories', 'url', 'info', 'grp', 'upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'stop': AdminDateWidget(attrs={'class': 'form-control mb-3'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grp'].initial = self.get_group_id()

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

# Task.objects.filter(groups__app__startswith='todo')