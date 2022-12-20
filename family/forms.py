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
        fields = ['name', 'sort', 'sour', 'sour_vers', 'sour_name', 'sour_corp', 'sour_data', 'sour_data_date', 'sour_data_copr', 
                  'dest', 'date', 'time', 'subm_id', 'file', 'copr', 'gedc_vers', 'gedc_form', 'gedc_form_vers', 'char', 'lang', 'note', 
                  'mh_id', 'mh_prj_id', 'mh_rtl',]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            'sort': forms.NumberInput(attrs={'class': 'form-control mb-2'}),
            'sour': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'sour_vers': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'sour_name': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'sour_corp': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'sour_data': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'sour_data_date': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'sour_data_copr': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}), 
            'dest': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'date': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'time': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'subm_id': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'file': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'copr': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'gedc_vers': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'gedc_form': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'gedc_form_vers': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'char': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'lang': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'note': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}), 
            'mh_id': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'mh_prj_id': forms.TextInput(attrs={'class': 'form-control mb-2'}), 
            'mh_rtl': forms.TextInput(attrs={'class': 'form-control mb-2'}),
        }


#----------------------------------
class EditIndividualForm(forms.ModelForm):
    class Meta:
        model = IndividualRecord
        fields = ['sex',]
        widgets = {
            'sex': forms.TextInput(attrs={'class': 'form-control mb-2'}),
        }

