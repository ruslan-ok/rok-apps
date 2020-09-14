from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.translation import gettext_lazy as _

from .models import Car, Fuel, Part, Repl


#----------------------------------
class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['name', 'plate', 'active']

#----------------------------------
class FuelForm(forms.ModelForm):
    pub_date = forms.SplitDateTimeField(widget = AdminSplitDateTime(), label = _('date').capitalize(), required = True)
    class Meta:
        model = Fuel
        fields = ['pub_date', 'odometr', 'volume', 'price', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows':3, 'cols':10, 'placeholder': _('add note').capitalize(), 'data-autoresize':''}),
        }

#----------------------------------
class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'chg_km', 'chg_mo', 'comment']

#----------------------------------
class ReplForm(forms.ModelForm):
    dt_chg = forms.SplitDateTimeField(widget = AdminSplitDateTime(), label = _('date').capitalize(), required = True)
    class Meta:
        model = Repl
        fields = ['part', 'name', 'dt_chg', 'odometr', 'name', 'manuf', 'part_num', 'comment']
    def __init__(self, car, *args, **kwargs):
        self.car = car
        super().__init__(*args, **kwargs)
        self.fields['part'].queryset = Part.objects.filter(car = car).order_by('name')

