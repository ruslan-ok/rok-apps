from dataclasses import dataclass, field
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from family.models import IndividualRecord, FamilyEventStructure, FamRecord
from family.views.life_date import EventDate
from family.descriptions.tags import TAGS

@dataclass
class DescriptorEvent():
    tag: str
    date: EventDate
    place: str
    indi: IndividualRecord
    relative: IndividualRecord
    role: str
    fam: FamRecord | None = field(init=False)
    role_name: str = field(init=False)
    relative_sex: str = field(init=False)

    def __post_init__(self):
        self.relative_sex = self.relative.get_sex()
        match self.role, self.relative_sex:
            case 'child', 'F':  self.role_name = _('daughter')
            case 'child', 'M':  self.role_name = _('son')
            case 'father', _:   self.role_name = _('father')
            case 'mother', _:   self.role_name = _('mother')
            case 'spouse', 'F': self.role_name = _('wife')
            case 'spouse', 'M': self.role_name = _('husband')
            case _: self.role_name = ''

    def get_place(self):
        return self.place
    
    def get_where(self):
        where = ''
        place = self.get_place()
        if place:
            where = f' {_("in")} {place}'
        return where
    
    def get_descr_indi_birth(self):
        father_name = ''
        father_age = ''
        mother_name = ''
        mother_age = ''
        father, mother = self.relative.get_parents()
        event_str_date = self.date.str_date
        if father:
            father_name = father.get_name()
            father_age = father.get_age(event_str_date)
            if not father_age:
                father_age = ''
            else:
                father_age = _(', age %(age)s') % {'age': father_age}
        if mother:
            mother_name = mother.get_name()
            mother_age = mother.get_age(event_str_date)
            if not mother_age:
                mother_age = ''
            else:
                mother_age = _(', age %(age)s') % {'age': mother_age}
        match self.relative_sex:
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
        return '%(name)s %(action)s %(when)s%(where)s%(parents_info)s.' % {
            'name': self.relative.get_name(), 
            'action': action,
            'when': self.date.when,
            'where': self.get_where(),
            'parents_info': parents_info,
        }
    
    def get_descr_indi_christ(self):
        return ''
    
    def get_descr_age(self, indi_sex: str, age: int | None, capitalize=False):
        if not age:
            return ''
        match indi_sex:
            case 'F': pronoun = pgettext_lazy('dative', 'she')
            case _: pronoun = pgettext_lazy('dative', 'he')
        if capitalize:
            return _('%(pronoun)s was %(age)s years old') % {'pronoun': pronoun.capitalize(), 'age': age}
        return _('when %(pronoun)s was %(age)s years old') % {'pronoun': pronoun, 'age': age}
    
    def get_descr_indi_death(self):
        age_descr = self.get_descr_age(self.indi.get_sex(), self.indi.get_age(self.date.str_date))
        if age_descr:
            age_descr = ' ' + age_descr
        match self.relative_sex:
            case 'F': action = pgettext_lazy('female', 'died')
            case _: action = pgettext_lazy('male', 'died')
        return '%(name)s %(action)s %(when)s%(where)s%(age_descr)s.' % {
            'name': self.relative.get_name(), 
            'action': action,
            'when': self.date.when,
            'where': self.get_where(),
            'age_descr': age_descr,
        }
    
    def get_descr_child_birth(self):
        match self.indi.get_sex():
            case 'F': pronoun = _('Her')
            case _: pronoun = _('His')
        match self.relative_sex:
            case 'F': action = pgettext_lazy('female', 'was born')
            case _: action = pgettext_lazy('male', 'was born')
        return _('%(pronoun)s %(role)s %(name)s %(action)s %(when)s%(where)s.') % {
            'pronoun': pronoun,
            'role': self.role_name,
            'name': self.relative.get_name('given'),
            'action': action,
            'when': self.date.when,
            'where': self.get_where(),
        }

    def get_descr_child_christ(self):
        return ''

    def get_descr_death(self):
        match self.indi.get_sex():
            case 'F': pronoun = _('Her')
            case _: pronoun = _('His')
        match self.relative_sex:
            case 'F': action = pgettext_lazy('female', 'passed away')
            case _: action = pgettext_lazy('male', 'passed away')
        return _('%(pronoun)s %(role)s %(name)s %(action)s %(when)s%(where)s at the age of %(age)s.') % {
            'pronoun': pronoun,
            'role': self.role_name,
            'name': self.relative.get_name('given'),
            'action': action,
            'when': self.date.when,
            'where': self.get_where(),
            'age': self.relative.get_age(self.date.str_date),
        }
    
    def get_descr_marriage(self):
        match self.indi.get_sex():
            case 'F': action = pgettext_lazy('female', 'married')
            case _: action = pgettext_lazy('male', 'married')
        where_descr = self.get_where()
        if where_descr:
            where_descr = where_descr + ', '
        age_descr = self.get_descr_age(self.indi.get_sex(), self.indi.get_age(self.date.str_date))
        if age_descr:
            age_descr = ', ' + age_descr + '.'
        return '%(self_name)s %(action)s %(spouse_name)s%(where)s%(when)s%(age)s' % {
            'self_name': self.indi.get_name(),
            'action': action,
            'spouse_name': self.relative.get_name(),
            'where': where_descr,
            'when': self.date.when,
            'age': age_descr,
        }
    
    def get_descr_marriage_date(self) -> str:
        if FamilyEventStructure.objects.filter(fam=self.fam, tag='MARR').exists():
            marr = FamilyEventStructure.objects.filter(fam=self.fam, tag='MARR').get()
            if marr.deta and marr.deta.date:
                ed = EventDate(marr.deta.date)
                return ed.str_date
        return ''

    def get_descr_divorce(self):
        duration = self.indi.get_age(self.date.str_date, self.get_descr_marriage_date())
        after = _('after %(duration)d years of marriage') % {'duration': duration}
        if after:
            after = ' ' + after
        age_descr = self.get_descr_age(self.indi.get_sex(), self.indi.get_age(self.date.str_date), capitalize=True)
        if age_descr:
            age_descr = ' ' + age_descr + '.'
        return '%(self_name)s %(and)s %(spouse_name)s %(action)s %(when)s%(where)s%(after)s.%(age)s' % {
            'self_name': self.indi.get_name(),
            'and': _('and'),
            'spouse_name': self.relative.get_name(),
            'action': _('were divorced'),
            'when': self.date.when,
            'where': self.get_where(),
            'after': after,
            'age': age_descr,
        }
    
    def get_event_descr(self):
        match self.role, self.tag:
            case 'indi', 'BIRT': ret = self.get_descr_indi_birth()
            case 'indi', 'CHR': ret = self.get_descr_indi_christ()
            case 'indi', 'DEAT': ret = self.get_descr_indi_death()
            case 'child', 'BIRT': ret = self.get_descr_child_birth()
            case 'child', 'CHR': ret = self.get_descr_child_christ()
            case _, 'DEAT': ret = self.get_descr_death()
            case _, 'MARR': ret = self.get_descr_marriage()
            case _, 'DIV': ret = self.get_descr_divorce()
            case _: ret = ''
        return ret.replace('..', '.')

    def get_event_title(self):
        title = TAGS.get(self.tag, self.tag)

        match self.role, self.relative_sex:
            case 'indi', _: role = ''
            case 'father', _: role = _('of father')
            case 'mother', _: role = _('of mother')
            case 'spouse', 'F': role = _('of wife')
            case 'spouse', 'M': role = _('of husband')
            case 'child', 'F': role = _('of daughter')
            case 'child', 'M': role = _('of son')
            case _: role = self.role

        ret = title
        if role and self.tag not in ('MARR', 'MARL', 'DIV'):
            ret = title + ' ' + role
        
        return ret

