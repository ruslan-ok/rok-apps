from dataclasses import dataclass
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from family.models import IndividualRecord, FamRecord, ChildToFamilyLink

@dataclass
class DescriptorIndi():
    indi: IndividualRecord

    def get_birth_info(self) -> str:
        name = self.indi.get_name()
        event = self.indi.get_event('BIRT')
        if not name or not event:
            return ''

        match self.indi.get_sex():
            case 'F': action = pgettext_lazy('female', 'was born')
            case _: action = pgettext_lazy('male', 'was born')

        ret = _('%(name)s %(action)s %(when_where)s') % {
            'name': self.indi.get_name(),
            'action': action,
            'when_where': event.get_when_where()
        }
        return ret
    
    def get_pronoun(self, genitive=False) -> str:
        match genitive, self.indi.get_sex():
            case False, 'F': pronoun = _('she')
            case False, 'M': pronoun = _('he')
            case True, 'F': pronoun = _('her')
            case True, 'M': pronoun = _('his')
            case _: pronoun = _('he')
        return pronoun
    
    def get_death_info(self) -> str:
        event = self.indi.get_event('DEAT')
        if not event:
            return ''
        age = 0
        event_date = event.get_event_date()
        if event_date:
            str_date = event_date['sort']
            age = self.indi.get_age(str_date)
        if age:
            age = ' ' + _('at the age of') + ' ' + str(age)

        match self.indi.get_sex():
            case 'F': action = pgettext_lazy('female', 'died')
            case _: action = pgettext_lazy('male', 'died')

        ret = _('%(pronoun)s %(action)s %(when)s%(age)s. ') % {
            'pronoun': self.get_pronoun().capitalize(),
            'action': action,
            'when': event.get_when(),
            'age': age,
        }
        return ret
    
    def get_parents_age(self) -> tuple[str, str]:
        birth_date = None
        birth = self.indi.get_event('BIRT')
        if birth:
            birth_date = birth.get_event_date()
        father_name = father_age = mother_name = mother_age = ''
        father, mother = self.indi.get_parents()
        if father:
            father_name = father.get_name()
            if birth_date and birth_date['sort']:
                father_age = father.get_age(birth_date['sort'])
        if mother:
            mother_name = mother.get_name()
            if birth_date and birth_date['sort']:
                mother_age = mother.get_age(birth_date['sort'])

        ret = ''
        if father_age and father_age == mother_age:
            ret = _(', %(pronoun)s father, %(father_name)s, and %(pronoun)s mother, %(mother_name)s, were %(father_age)d. ') % {
                'pronoun': self.get_pronoun(True),
                'father_name': father_name,
                'mother_name': mother_name,
                'father_age': father_age,
            }
        else:
            if father_age and mother_age:
                ret = _(', %(pronoun)s father, %(father_name)s, was %(father_age)d and %(pronoun)s mother, %(mother_name)s, was %(mother_age)d. ') % {
                    'pronoun': self.get_pronoun(True),
                    'father_name': father_name,
                    'mother_name': mother_name,
                    'father_age': father_age,
                    'mother_age': mother_age,
                }
            if father_age and not mother_age:
                ret = _(', %(pronoun)s father, %(father_name)s, was %(father_age)d. ') % {
                    'pronoun': self.get_pronoun(True),
                    'father_name': father_name,
                    'father_age': father_age,
                }
            if not father_age and mother_age:
                ret = _(', %(pronoun)s mother, %(mother_name)s, was %(mother_age)d. ') % {
                    'pronoun': self.get_pronoun(True),
                    'mother_name': mother_name,
                    'mother_age': mother_age,
                }
        prefix = ''
        if ret:
            prefix = _("When") + ' '
        if not ret:
            ret = '. '
        return prefix, ret
    
    def get_spouses_and_children(self):
        ret = []
        match self.indi.get_sex():
            case 'F':   indi_fams = FamRecord.objects.filter(wife=self.indi.id)
            case _:     indi_fams = FamRecord.objects.filter(husb=self.indi.id)
        for fam in indi_fams:
            children = ChildToFamilyLink.objects.filter(fami=fam.id)
            match self.indi.get_sex():
                case 'F':   spouse = fam.husb
                case _:     spouse = fam.wife
            spouse_name = ''
            if spouse:
                spouse_name = spouse.get_name()
            ret.append({'spouse_name': spouse_name, 'child_num': len(children)})
        return ret
    
    def get_indi_children(self, birth_info: str) -> str:
        ret = ''
        is_fem = self.indi.get_sex() == 'F'
        is_info = (birth_info != '')
        is_first = True
        fams = self.get_spouses_and_children()
        for fam in fams:
            spouse_name = fam['spouse_name']
            if ret:
                ret += _("and") + ' '
            else:
                match is_first, is_fem, is_info:
                    case True, True, True:  ret += _("She has") + ' '
                    case True, False, True: ret += _("He has") + ' '
                    case True, _, False:    ret += self.indi.get_name() + ' ' + _("has") + ' '
                    case False, _, _:       ret += ''

            match fam['child_num']:
                case 0: ret += _('no children')
                case 1: ret += _('one child')
                case 2: ret += _('two children')
                case 3: ret += _('three children')
                case 4: ret += _('four children')
                case 5: ret += _('five children')
                case _: ret += fam["child_num"] + ' ' + _("children")
            if not spouse_name:
                spouse_name = _('unknown partner')
            ret += ' ' + _("with") + ' ' + spouse_name
            is_first = False
        if ret:
            ret += '. '
        return ret

    def get_biography(self) -> str:
        birth_info = self.get_birth_info()
        death_info = self.get_death_info()
        prefix, parents_age = self.get_parents_age()
        indi_children = self.get_indi_children(birth_info)
        ret = prefix + birth_info + parents_age + indi_children + death_info
        if not ret and self.indi.get_name():
            ret = _('There is no information about %(name)s.') % {'name': self.indi.get_name()}
        return ret
    
