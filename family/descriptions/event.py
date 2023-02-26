from dataclasses import dataclass
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from family.ged4py.date import DateValue
from family.models import IndividualRecord, IndividualEventStructure

@dataclass
class DescriptorEvent():
    indi: IndividualRecord
    role: str
    event: IndividualEventStructure

    def get_str_date(self):
        if self.event.deta:
            ev_date = DateValue.parse(self.event.deta.date)
            if ev_date:
                return ev_date.get_str_date()
        return ''

    def get_place(self):
        place = ''
        if self.event.deta and self.event.deta.plac:
            place = self.event.deta.plac.name
        return place
    
    def get_where(self):
        where = ''
        place = self.get_place()
        if place:
            where = f' {_("in")} {place}'
        return where
    
    def get_descr_indi_birth(self, date):
        father_name = ''
        father_age = ''
        mother_name = ''
        mother_age = ''
        father, mother = self.indi.get_parents()
        event_str_date = self.get_str_date()
        if father:
            father_name = father.get_name()
            father_age = father.get_age(event_str_date)
            if not father_age:
                father_age = ''
            else:
                father_age = _(', age s%(age)s') % {'age': father_age}
        if mother:
            mother_name = mother.get_name()
            mother_age = mother.get_age(event_str_date)
            if not mother_age:
                mother_age = ''
            else:
                mother_age = _(', age s%(age)s') % {'age': mother_age}
        match self.indi.get_sex():
            case 'F': action = pgettext_lazy('female', 'was born')
            case _: action = pgettext_lazy('male', 'was born')
        parents_info = ''
        if father and mother:
            parents_info = _(', to %(mother_name)s%(mother_age)s, and %(father_name)s%(father_age)s') % {
                'mother_name': mother_name,
                'mother_age': mother_age,
                'father_name': father_name,
                'father_age': father_age,
            }
        ret = '%(name)s %(action)s %(when)s%(where)s%(parents_info)s.' % {
            'name': self.indi.get_name(), 
            'action': action,
            'when': date['when'],
            'where': self.get_where(),
            'parents_info': parents_info,
        }
        return ret
    
    def get_descr_indi_death(self, date):
        match self.indi.get_sex():
            case 'F': pronoun = pgettext_lazy('dative', 'she')
            case _: pronoun = pgettext_lazy('dative', 'he')
        match self.indi.get_sex():
            case 'F': action = pgettext_lazy('female', 'died')
            case _: action = pgettext_lazy('male', 'died')
        ret = _('%(name)s %(action)s %(when)s%(where)s when %(pronoun)s was %(age)s years old.') % {
            'name': self.indi.get_name(), 
            'action': action,
            'when': date['when'],
            'where': self.get_where(),
            'pronoun': pronoun,
            'age': self.indi.get_age(date['sort']),
        }
        return ret
    
    def get_descr_child_birth(self, date, indi):
        match indi.get_sex():
            case 'F': pronoun = _('Her')
            case _: pronoun = _('His')
        match self.indi.get_sex():
            case 'F': role = _('daughter')
            case _: role = _('son')
        match self.indi.get_sex():
            case 'F': action = pgettext_lazy('female', 'was born')
            case _: action = pgettext_lazy('male', 'was born')
        ret = _('%(pronoun)s %(role)s %(name)s %(action)s %(when)s%(where)s.') % {
            'pronoun': pronoun,
            'role': role,
            'name': self.indi.get_name('given'),
            'action': action,
            'when': date['when'],
            'where': self.get_where(),
        }
        return ret

    def get_descr_death(self, date, indi, role):
        match indi.get_sex():
            case 'F': pronoun = _('Her')
            case _: pronoun = _('His')
        match self.indi.get_sex():
            case 'F': action = pgettext_lazy('female', 'passed away')
            case _: action = pgettext_lazy('male', 'passed away')
        ret = _('%(pronoun)s %(role)s %(name)s %(action)s %(when)s%(where)s at the age of %(age)s.') % {
            'pronoun': pronoun,
            'role': role,
            'name': self.indi.get_name('given'),
            'action': action,
            'when': date['when'],
            'where': self.get_where(),
            'age': self.indi.get_age(date['sort']),
        }
        return ret
    
    def get_descr(self, date, indi):
        ret = '???'
        match self.role, self.indi.get_sex(), self.event.tag:
            case 'indi', _, 'BIRT': ret = self.get_descr_indi_birth(date)
            case 'indi', _, 'DEAT': ret = self.get_descr_indi_death(date)
            case 'child', _, 'BIRT': ret = self.get_descr_child_birth(date, indi)
            case 'child', 'F', 'DEAT': ret = self.get_descr_death(date, indi, _('daughter'))
            case 'child', 'M', 'DEAT': ret = self.get_descr_death(date, indi, _('son'))
            case 'father', _, 'DEAT': ret = self.get_descr_death(date, indi, _('father'))
            case 'mother', _, 'DEAT': ret = self.get_descr_death(date, indi, _('mother'))
            case 'spouse', 'F', 'DEAT': ret = self.get_descr_death(date, indi, _('wife'))
            case 'spouse', 'M', 'DEAT': ret = self.get_descr_death(date, indi, _('husband'))
            case _: ret = '?'
        return ret
