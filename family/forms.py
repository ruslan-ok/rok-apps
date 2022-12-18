from django import forms
from django.utils.translation import gettext_lazy as _
from family.config import app_config
from family.models import (FamTree, IndividualRecord, IndiInfo, FamRecord, MultimediaRecord, RepositoryRecord, SourceRecord, SubmitterRecord, 
    ChildToFamilyLink, NoteStructure,)
from rusel.widgets import InlineRadio

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
class CreateIndiForm(forms.ModelForm):

    class Meta:
        model = IndividualRecord
        fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = app_config
        self.role = None
        
    def save(self, commit=True):
        ret = super().save(commit=False)
        ret.save()
        return ret

#----------------------------------
SEX_CHOICES = [
    ('M', _('male').capitalize()),
    ('F', _('female').capitalize()),
    ('U', _('unknown').capitalize()),
]

ALIVE_CHOICES = [
    ('L', _('living').capitalize()),
    ('D', _('deceased').capitalize()),
]

class EditIndiEssentials(forms.ModelForm):
    sex = forms.ChoiceField(label='', choices=SEX_CHOICES, widget=InlineRadio)
    alive = forms.ChoiceField(label='', choices=ALIVE_CHOICES, widget=InlineRadio)
    class Meta:
        model = IndiInfo
        fields = ['givn', 'surn', 'sex', 'birth_date', 'birth_place', 'alive', 'death_date', 'death_place']
        widgets = {
            'givn': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'surn': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'birth_date': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'birth_place': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'death_date': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'death_place': forms.TextInput(attrs={'class': 'form-control mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = app_config
        self.role = None
        
    def save(self, commit=True):
        ret = super().save(commit=False)
        ret.save()
        return ret


#----------------------------------
PEDI_COICES = [
    ('adopted', _('adopted').capitalize()),
    ('birth', _('birth').capitalize()),
    ('foster', _('foster').capitalize()),
]

class EditIndiFamily(forms.ModelForm):
    rela = forms.ChoiceField(choices=PEDI_COICES)
    class Meta:
        model = ChildToFamilyLink
        fields = ['rela', ]
        widgets = {
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = app_config
        self.role = None
        
    def save(self, commit=True):
        ret = super().save(commit=False)
        ret.save()
        return ret


#----------------------------------
class CreateFamForm(forms.ModelForm):

    class Meta:
        model = FamRecord
        fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = app_config
        self.role = None
        
    def save(self, commit=True):
        ret = super().save(commit=False)
        ret.save()
        return ret

#----------------------------------
class CreateMediaForm(forms.ModelForm):

    class Meta:
        model = MultimediaRecord
        fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = app_config
        self.role = None
        
    def save(self, commit=True):
        ret = super().save(commit=False)
        ret.save()
        return ret

#----------------------------------
class CreateRepoForm(forms.ModelForm):

    class Meta:
        model = RepositoryRecord
        fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = app_config
        self.role = None
        
    def save(self, commit=True):
        ret = super().save(commit=False)
        ret.save()
        return ret

#----------------------------------
class CreateNoteForm(forms.ModelForm):

    class Meta:
        model = NoteStructure
        fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = app_config
        self.role = None
        
    def save(self, commit=True):
        ret = super().save(commit=False)
        ret.save()
        return ret

#----------------------------------
class CreateSourceForm(forms.ModelForm):

    class Meta:
        model = SourceRecord
        fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = app_config
        self.role = None
        
    def save(self, commit=True):
        ret = super().save(commit=False)
        ret.save()
        return ret

#----------------------------------
class CreateSubmitterForm(forms.ModelForm):

    class Meta:
        model = SubmitterRecord
        fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = app_config
        self.role = None
        
    def save(self, commit=True):
        ret = super().save(commit=False)
        ret.save()
        return ret

