from django import forms

from .models import Car, Fuel, Part, Repl


#----------------------------------
class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['name', 'plate', 'active']

#----------------------------------
class FuelForm(forms.ModelForm):
    class Meta:
        model = Fuel
        fields = ['pub_date', 'odometr', 'volume', 'price', 'comment']

#----------------------------------
class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'chg_km', 'chg_mo', 'comment']

#----------------------------------
class ReplForm(forms.ModelForm):
    class Meta:
        model = Repl
        fields = ['part', 'name', 'dt_chg', 'odometr', 'name', 'manuf', 'part_num', 'comment']
