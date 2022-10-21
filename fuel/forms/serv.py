from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task
from task.const import NUM_ROLE_PART, ROLE_SERVICE
from fuel.config import app_config
from rusel.widgets import DateInput, UrlsInput, CategoriesInput, Select

role = ROLE_SERVICE

#----------------------------------
class CreateForm(BaseCreateForm):

    new_part = forms.ChoiceField(
        label=False,
        required=True,
        widget=Select(attrs={'label': _('Car part'), 'class': 'col-md-3'}))

    class Meta:
        model = Task
        fields = ['new_part']

    def __init__(self, nav_item, user_id, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        part_choices = []
        for part in Task.objects.filter(user=user_id, app_fuel=NUM_ROLE_PART, task_1=nav_item.id):
            part_choices.append((part.id, part.name),)
        self.fields['new_part'].choices = part_choices
        
#----------------------------------
class EditForm(BaseEditForm):
    car_odometr = forms.IntegerField(
        label=_('Odometer'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Odometer value')}))
    event = forms.DateTimeField(
        required=True,
        widget=DateInput(format='%Y-%m-%dT%H:%M', attrs={'label': _('Event date'), 'type': 'datetime-local'}))
    task_2 = forms.ModelChoiceField(
        label=_('Spare part'),
        required=True,
        queryset=Task.objects.filter(app_fuel=NUM_ROLE_PART).order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control select mb-3'}))
    repl_manuf = forms.CharField(
        label=_('Manufacturer'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    repl_part_num = forms.CharField(
        label=_('Catalog number'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    repl_descr = forms.CharField(
        label=_('Name'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add link')}))
    categories = forms.CharField(
        label=_('Categories'),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add category')}))
    latitude = forms.HiddenInput()
    longitude = forms.HiddenInput()

    class Meta:
        model = Task
        fields = ['car_odometr', 'event', 'task_2', 'repl_manuf', 'repl_part_num', 'repl_descr', 'info', 'url', 'categories', 'upload', 'latitude', 'longitude']
        widgets = {
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.fields['task_2'].queryset = Task.objects.filter(user=self.instance.user.id, app_fuel=NUM_ROLE_PART, task_1=self.instance.task_1.id).order_by('name')

