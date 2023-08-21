from django import forms
from django.utils.translation import gettext_lazy as _
from family.models import FamTree, IndividualRecord

#----------------------------------
class CreateFamTreeForm(forms.ModelForm):
    class Meta:
        model = FamTree
        fields = ['name', 'sort']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            'sort': forms.NumberInput(attrs={'class': 'form-control mb-2'}),
        }

#----------------------------------
class EditFamTreeForm(forms.ModelForm):
    class Meta:
        model = FamTree
        fields = ['name', 'sour', 'sour_vers', 'sour_name', 'sour_corp', 'sour_data', 'sour_data_date', 'sour_data_copr', 
                  'dest', 'date', 'time', 'file', 'copr', 'gedc_vers', 'gedc_form', 'char', 'char_vers', 'lang', 'note', 
                  'mh_id', 'mh_prj_id', 'mh_rtl',]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            #'sort': forms.NumberInput(attrs={'class': 'form-control mb-2'}),
            'sour': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'sour_vers': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'sour_name': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'sour_corp': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'sour_data': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'sour_data_date': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'sour_data_copr': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':'', 'readonly': True}), 
            'dest': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'date': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'time': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            #'subm_id': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'file': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'copr': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'gedc_vers': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'gedc_form': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'char': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'char_vers': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'lang': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'note': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}), 
            'mh_id': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'mh_prj_id': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}), 
            'mh_rtl': forms.TextInput(attrs={'class': 'form-control mb-2', 'readonly': True}),
        }


#----------------------------------
class EditIndividualForm(forms.ModelForm):
    class Meta:
        model = IndividualRecord
        fields = ['sex',]
        widgets = {
            'sex': forms.TextInput(attrs={'class': 'form-control mb-2'}),
        }

