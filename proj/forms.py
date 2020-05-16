from django import forms

from .models import Direct, Proj


#----------------------------------
class DirectForm(forms.ModelForm):
    class Meta:
        model = Direct
        fields = ['name', 'active']

#----------------------------------
class ProjForm(forms.ModelForm):
    class Meta:
        model = Proj
        fields = ['date', 'kol', 'price', 'course', 'usd', 'kontr', 'text']
