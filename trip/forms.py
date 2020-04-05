from django.forms import ModelForm, ChoiceField, DecimalField, BooleanField
from .models import Person, Trip
from django.utils.translation import gettext, gettext_lazy as _
from django.core.exceptions import ValidationError

class TripFormBase(ModelForm):

    class Meta:
        model = Trip
        fields = ['year', 'week', 'days', 'oper', 'price', 'driver', 'passenger', 'text', 'modif',]


class TripForm(TripFormBase):

    summa = DecimalField(label = _('summa').capitalize())
    day_11 = BooleanField(label = 'day_11', required = False)
    day_12 = BooleanField(label = 'day_12', required = False)
    day_13 = BooleanField(label = 'day_13', required = False)
    day_14 = BooleanField(label = 'day_14', required = False)
    day_15 = BooleanField(label = 'day_15', required = False)
    day_16 = BooleanField(label = 'day_16', required = False)
    day_17 = BooleanField(label = 'day_17', required = False)
    day_21 = BooleanField(label = 'day_21', required = False)
    day_22 = BooleanField(label = 'day_22', required = False)
    day_23 = BooleanField(label = 'day_23', required = False)
    day_24 = BooleanField(label = 'day_24', required = False)
    day_25 = BooleanField(label = 'day_25', required = False)
    day_26 = BooleanField(label = 'day_26', required = False)
    day_27 = BooleanField(label = 'day_27', required = False)

    class Meta(TripFormBase.Meta):
        fields = TripFormBase.Meta.fields + ['summa',
                                             'day_11', 'day_12', 'day_13', 'day_14', 'day_15', 'day_16', 'day_17',
                                             'day_21', 'day_22', 'day_23', 'day_24', 'day_25', 'day_26', 'day_27',
                                             ]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['days'].hidden = True
        self.fields['modif'].hidden = True
        self.fields['driver'].queryset = Person.objects.filter(user = user).order_by('name')
        self.fields['passenger'].queryset = Person.objects.filter(user = user).order_by('name')
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['summa'].widget.attrs['readonly'] = True

    def clean_year(self):
        data = self.cleaned_data['year']
        if (data < 2000) or (data > 2100):
            self.add_error('year', 'Ожидался год в диапазоне от 2000 до 2100')
        return data
            
    def clean_week(self):
        data = self.cleaned_data['week']
        if (data < 1) or (data > 53):
            self.add_error('week', 'Ожидался номер недели в диапазоне от 1 до 53')
        return data
            
    def clean_price(self):
        data = self.cleaned_data['price']
        if (data == 0):
            self.add_error('price', 'Цена должна быть указана')
        return data
            
    def clean(self):
        super().clean()
        if (self.cleaned_data['driver'] == self.cleaned_data['passenger']):
            self.add_error('passenger', 'Укажите другого пассажира')
            raise  ValidationError('Водитель и Пассажир должны отличаться')

        self.cleaned_data['days'] = 0
        for i in range(2):
            for j in range(7):
                if self.cleaned_data['day_' + str(i+1) + str(j+1)]:
                    self.cleaned_data['days'] = self.cleaned_data['days'] + (1 << (i+j*2))
        if (self.cleaned_data['oper'] == 0) and (self.cleaned_data['days'] == 0):
            raise  ValidationError('Не отмечены дни недели')


class PersonForm(ModelForm):

    class Meta:
        model = Person
        exclude = ('user',)
