import os, shutil
from datetime import datetime
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.utils.formats import date_format
from django.urls import reverse
from django.db import models
from django.db.models.signals import pre_delete 
from django.dispatch import receiver
from family.ged4py.date import DateValue
from family.const import *

#--------------------------------------------------
class AddressStructure(models.Model):
    addr = models.CharField(_('Address value'), max_length=500, blank=True, null=True)
    addr_adr1 = models.CharField(_('Address line 1'), max_length=60, blank=True, null=True)
    addr_adr2 = models.CharField(_('Address line 2'), max_length=60, blank=True, null=True)
    addr_adr3 = models.CharField(_('Address line 3'), max_length=60, blank=True, null=True)
    addr_city = models.CharField(_('City'), max_length=60, blank=True, null=True)
    addr_stae = models.CharField(_('State'), max_length=60, blank=True, null=True)
    addr_post = models.CharField(_('Postal code'), max_length=10, blank=True, null=True)
    addr_ctry = models.CharField(_('Country'), max_length=60, blank=True, null=True)
    phon = models.CharField(_('Phone number'), max_length=25, blank=True, null=True)
    phon2 = models.CharField(_('Phone number 2'), max_length=25, blank=True, null=True)
    phon3 = models.CharField(_('Phone number 3'), max_length=25, blank=True, null=True)
    email = models.CharField(_('Email'), max_length=120, blank=True, null=True)
    email2 = models.CharField(_('Email 2'), max_length=120, blank=True, null=True)
    email3 = models.CharField(_('Email 3'), max_length=120, blank=True, null=True)
    fax = models.CharField(_('Fax'), max_length=60, blank=True, null=True)
    fax2 = models.CharField(_('Fax 2'), max_length=60, blank=True, null=True)
    fax3 = models.CharField(_('Fax 3'), max_length=60, blank=True, null=True)
    www = models.CharField(_('Web page'), max_length=2047, blank=True, null=True)
    www2 = models.CharField(_('Web page 2'), max_length=2047, blank=True, null=True)
    www3 = models.CharField(_('Web page 3'), max_length=2047, blank=True, null=True)
    owner = models.CharField(_('Owner of this record'), max_length=20, blank=True, null=True)

class ChangeDate(models.Model):
    date_time = models.DateTimeField(_('Change date-time'), blank=True, null=True)
    date = models.CharField(_('Date'), max_length=20, blank=True, null=True)
    time = models.CharField(_('Time'), max_length=20, blank=True, null=True)
    owner = models.CharField(_('Owner of this record'), max_length=20, blank=True, null=True)

    def __str__(self):
        d = self.get_date()
        t = self.get_time()
        return (d if d else '') + (' ' if d and t else '') + (t if t else '')

    def get_date(self):
        if self.date_time:
            return self.date_time.strftime('%d %b %Y')
        else:
            if self.date:
                return self.date
                # format_visitor = DateFormatter()
                # return self.date.accept(format_visitor)
        return None

    def get_time(self):
        if self.date_time:
            return self.date_time.strftime('%H:%M:%S.%f')
        else:
            return self.time

#--------------------------------------------------
class FamTree(models.Model):
    sour = models.CharField(_('System ID'), max_length=50, blank=True, null=True)
    sour_vers = models.CharField(_('Version number'), max_length=15, blank=True, null=True)
    sour_name = models.CharField(_('Name of product'), max_length=90, blank=True, null=True)
    sour_corp = models.CharField(_('Name of business'), max_length=90, blank=True, null=True)
    sour_corp_addr = models.ForeignKey(AddressStructure, on_delete=models.SET_NULL, verbose_name=_('Business address'), related_name='business_address', null=True)
    sour_data = models.CharField(_('Name of source data'), max_length=90, blank=True, null=True)
    sour_data_date = models.DateTimeField(_('Publication date'), blank=True, null=True)
    sour_data_copr = models.TextField(_('Copyright source data'), blank=True, null=True)
    dest = models.CharField(_('Receiving system name'), max_length=20, blank=True, null=True)
    date = models.CharField(_('Transmission date'), max_length=11, blank=True, null=True)
    time = models.CharField(_('Time value'), max_length=12, blank=True, null=True)
    subm_id = models.IntegerField(_('Submitter reference'), blank=True, null=True)
    file = models.CharField(_('File name'), max_length=90, blank=True, null=True)
    copr = models.CharField(_('Copyright gedcom file'), max_length=90, blank=True, null=True)
    gedc_vers = models.CharField(_('Gedcom version number'), max_length=15, blank=True, null=True)
    gedc_form = models.CharField(_('Gedcom form'), max_length=20, blank=True, null=True)
    char_vers = models.CharField(_('Character set version number'), max_length=15, blank=True, null=True)
    char = models.CharField(_('Character set'), max_length=12, blank=True, null=True)
    lang = models.CharField(_('Language of text'), max_length=15, blank=True, null=True)
    note = models.TextField(_('Gedcom content description'), blank=True, null=True)
    mh_id = models.CharField(_('ID in MyHeritage.com'), max_length=50, blank=True, null=True)
    mh_prj_id = models.CharField(_('Project GUID'), max_length=200, blank=True, null=True)
    mh_rtl = models.CharField(_('Source RTL'), max_length=200, blank=True, null=True)
    sort = models.IntegerField(_('Sorting position'), null=True)
    created = models.DateTimeField(_('Creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('Last modification time'), blank=True, auto_now=True)
    mark = models.CharField(_('Debug marker'), max_length=20, blank=True, null=True)
    cur_indi = models.IntegerField(_('Current individual id'), null=True)
    name = models.CharField(_('Family tree name'), max_length=200, blank=True, null=True)
    depth = models.IntegerField(_('Tree depth'), default=0, null=True)

    def __str__(self):
        return self.name

    def s_id(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('family:pedigree-detail', args=(self.id,))

    def before_delete(self):
        Gedcom.objects.filter(tree=self.id).delete()
        if self.sour_corp_addr:
            self.sour_corp_addr.delete()
        for item in SubmitterRecord.objects.filter(tree=self.id):
            item.before_delete()
        for item in AlbumRecord.objects.filter(tree=self.id):
            item.before_delete()
        for item in IndividualRecord.objects.filter(tree=self.id):
            item.before_delete()
        for item in FamRecord.objects.filter(tree=self.id):
            item.before_delete()
        for item in MultimediaRecord.objects.filter(tree=self.id):
            item.before_delete()
        for item in SourceRecord.objects.filter(tree=self.id):
            item.before_delete()
        for item in RepositoryRecord.objects.filter(tree=self.id):
            item.before_delete()
        for item in NoteRecord.objects.filter(tree=self.id):
            item.before_delete()

    def delete_gedcom_file(self, user):
        folder = FamTree.get_import_path()
        if folder and self.file:
            filepath = folder + self.file
            if os.path.exists(filepath):
                if os.path.exists(filepath + '_media'):
                    shutil.rmtree(filepath + '_media')
                os.remove(filepath)
        filepath = self.get_export_file(user)
        if filepath and os.path.exists(filepath):
            os.remove(filepath)

    def is_leaf(self):
        return True

    def store_name(self):
        name = self.name
        if not name and self.file:
            pos = self.file.rfind('.')
            if pos:
                name = self.file[:pos]
            else:
                name = self.file
        return name

    def get_file_name(self):
        fname = self.file
        if not fname:
            if self.name:
                fname = f'{self.name}.ged'
            else:
                fname = f'family_tree_{self.id}.ged'
        if (fname[-4:] != '.ged' and fname[-4:] != '.GED'):
            fname += '.ged'
        return fname

    @classmethod
    def get_import_path(cls):
        folder = os.environ.get('FAMILY_STORAGE_PATH', '') + '\\pedigree\\'
        if not os.path.exists(folder):
            os.mkdir(folder)
        return folder

    def get_export_path(self, user):
        folder = os.environ.get('DJANGO_STORAGE_PATH', '').format(user.username) + 'family\\'
        if not os.path.exists(folder):
            os.mkdir(folder)
        return folder

    def get_export_file(self, user):
        folder = self.get_export_path(user)
        fname = self.get_file_name()
        if os.path.exists(folder + fname):
            return folder + fname
        return None

@receiver(pre_delete)
def delete_fam_tree(sender, instance, **kwargs):
    if type(instance) == FamTree:
        instance.before_delete()

#--------------------------------------------------
class FamTreePermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'), related_name = 'famtree_permission_user')
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('Family tree'), related_name='famtree_permission_tree')
    can_view = models.BooleanField('Can view family tree', default=False)
    can_clone = models.BooleanField('Can clone family tree', default=False)
    can_change = models.BooleanField('Can change family tree', default=False)
    can_delete = models.BooleanField('Can delete family tree', default=False)
    can_merge = models.BooleanField('Can merge family tree', default=False)

    def __str__(self):
        perm = ''
        if self.can_view:
            perm += 'V'
        else:
            perm += '-'
        if self.can_clone:
            perm += 'C'
        else:
            perm += '-'
        if self.can_change:
            perm += 'E'
        else:
            perm += '-'
        if self.can_delete:
            perm += 'D'
        else:
            perm += '-'
        if self.can_merge:
            perm += 'M'
        else:
            perm += '-'
        return f'{self.user.username} - {self.tree.name}: [{perm}]'


class FamTreeUser(models.Model):
    user_id = models.IntegerField(_('User id'), null=False)
    can_view = models.BooleanField('Can view family tree', default=False)
    can_clone = models.BooleanField('Can clone family tree', default=False)
    can_change = models.BooleanField('Can change family tree', default=False)
    can_delete = models.BooleanField('Can delete family tree', default=False)
    can_merge = models.BooleanField('Can merge family tree', default=False)
    tree_id = models.IntegerField(_('Tree id'), null=False)
    sour = models.CharField(_('The ID of the system that created this dataset'), max_length=50, blank=True, null=True)
    sour_vers = models.CharField(_('Source system version number'), max_length=15, blank=True, null=True)
    sour_name = models.CharField(_('Name of product'), max_length=90, blank=True, null=True)
    sour_corp = models.CharField(_('Name of business'), max_length=90, blank=True, null=True)
    sour_corp_addr_id = models.IntegerField(_('Manufacturer address identifier'), null=False)
    sour_data = models.CharField(_('Name of source data'), max_length=90, blank=True, null=True)
    sour_data_date = models.DateField(_('Publication date'), blank=True, null=True)
    sour_data_copr = models.TextField(_('Copyright source data'), blank=True, null=True)
    dest = models.CharField(_('Receiving system name'), max_length=20, blank=True, null=True)
    date = models.CharField(_('Transmission date'), max_length=11, blank=True, null=True)
    time = models.CharField(_('Time value'), max_length=12, blank=True, null=True)
    subm_id = models.IntegerField(_('Submitter reference'), blank=True, null=True)
    file = models.CharField(_('File name'), max_length=90, blank=True, null=True)
    copr = models.CharField(_('Copyright GEDCOM file'), max_length=90, blank=True, null=True)
    gedc_vers = models.CharField(_('GEDCOM version number'), max_length=15, blank=True, null=True)
    gedc_form = models.CharField(_('gedcom form'), max_length=20, blank=True, null=True)
    char = models.CharField(_('Character set'), max_length=12, blank=True, null=True)
    char_vers = models.CharField(_('Character set version number'), max_length=15, blank=True, null=True)
    lang = models.CharField(_('Language of text'), max_length=15, blank=True, null=True)
    note = models.TextField(_('Gedcom content description'), blank=True, null=True)
    mh_id = models.CharField(_('ID in MyHeritage.com'), max_length=50, blank=True, null=True)
    mh_prj_id = models.CharField(_('Project GUID'), max_length=200, blank=True, null=True)
    mh_rtl = models.CharField(_('Source RTL'), max_length=200, blank=True, null=True)
    sort = models.IntegerField(_('Sorting position'), null=True)
    created = models.DateTimeField(_('Creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('Last modification time'), blank=True, auto_now=True)
    mark = models.CharField(_('Debug marker'), max_length=20, blank=True, null=True)
    cur_indi_id = models.IntegerField(_('Current individual id'), null=True)
    name = models.CharField(_('Family tree name'), max_length=200, blank=True, null=True)
    depth = models.IntegerField(_('Tree depth'), default=0, null=True)

    class Meta:
        managed = False
        db_table = 'family_vw_famtree'

    def get_absolute_url(self):
        return reverse('family:pedigree-detail', args=(self.tree_id,))
    
    def set_active(self, user):
        if FamTree.objects.filter(id=self.tree_id).exists():
            tree = FamTree.objects.filter(id=self.tree_id).get()
            Params.set_cur_tree(user, tree)


#--------------------------------------------------
class IndividualRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('Tree header'), related_name='individual_tree_header', null=True)
    xref = models.IntegerField(_('Identifier in the source system'), null=True)
    sex = models.CharField(_('Sex'), max_length=1, blank=True, null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('Change date'), related_name='individual_change_date', null=True)
    _upd = models.CharField(_('Custom field: update'), max_length=40, blank=True, null=True)
    _uid = models.CharField(_('Custom field: uid'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def __str__(self):
        return self.get_name()

    def get_absolute_url(self):
        return reverse('family:individual-detail', args=(self.tree.id, self.id,))

    def before_delete(self):
        for item in IndividualEventStructure.objects.filter(indi=self.id):
            item.before_delete()
        for item in IndividualAttributeStructure.objects.filter(indi=self.id):
            item.before_delete()
        for item in PersonalNameStructure.objects.filter(indi=self.id):
            item.before_delete()
        if self.chan:
            self.chan.delete()

    def get_id(self):
        if type(self.id) == int:
            return self.id
        return self.id.id

    def get_name(self, part='full'):
        ret = ''
        if PersonalNameStructure.objects.filter(indi=self.get_id()).exists():
            pns = PersonalNameStructure.objects.filter(indi=self.get_id())[0]
            if pns.piec:
                match part:
                    case 'given':
                        if pns.piec.givn:
                            ret = pns.piec.givn
                    case 'surname':
                        if pns.piec.surn:
                            ret = pns.piec.surn
                    case _:
                        if pns.piec.givn:
                            ret = pns.piec.givn
                        if pns.piec.surn:
                            if ret:
                                ret += ' '
                            ret += pns.piec.surn
        return ret
    
    def name(self):
        return self.get_name()

    def get_sex(self):
        if type(self.sex) == str:
            sex = self.sex
        else:
            sex = self.id.sex
        if sex:
            return sex
        return 'M'

    def get_parents_family(self):
        fams = ChildToFamilyLink.objects.filter(chil=self.get_id())
        if len(fams):
            return fams[0].fami
        return None

    def get_parents(self):
        family = self.get_parents_family()
        if family:
            return family.husb, family.wife
        return None, None
    
    def get_families(self):
        if self.get_sex() == 'F':
            return FamRecord.objects.filter(wife=self.get_id())
        return FamRecord.objects.filter(husb=self.get_id())
    
    def get_spouses(self):
        ret = []
        families = self.get_families()
        for family in families:
            if self.get_sex() == 'F':
                ret.append(family.husb)
            else:
                ret.append(family.wife)
        return ret

    def get_children(self):
        ret = []
        families = self.get_families()
        for family in families:
            for ctfl in ChildToFamilyLink.objects.filter(fami=family.id):
                    ret.append(ctfl.chil)
        return ret
    
    def get_events(self):
        return IndividualEventStructure.objects.filter(indi=self.get_id())

    def get_event(self, tag):
        if IndividualEventStructure.objects.filter(indi=self.get_id(), tag=tag).exists():
            return IndividualEventStructure.objects.filter(indi=self.get_id(), tag=tag).get()
        return None

    def get_age(self, event_str_date, birth_str_date=None):
        if not birth_str_date:
            birth = self.get_event('BIRT')
            if birth and birth.deta:
                ev_date = DateValue.parse(birth.deta.date)
                if ev_date:
                    birth_str_date = ev_date.get_str_date()
        if not birth_str_date or not event_str_date:
            return None
        d1 = d2 = y1 = y2 = None
        try:
            d1 = datetime.strptime(birth_str_date, '%Y-%m-%d')
        except:
            try:
                y1 = int(birth_str_date)
            except:
                pass
        try:
            d2 = datetime.strptime(event_str_date, '%Y-%m-%d')
        except:
            try:
                y2 = int(event_str_date)
            except:
                pass
        if d1 and d2:
            age = d2.year - d1.year
            dt = datetime(d1.year, d2.month, d2.day)
            if dt < d1:
                age -= 1
            return age
        if d1 and not y1:
            y1 = d1.year
        if d2 and not y2:
            y2 = d2.year
        if y1 and y2:
            return y2 - y1
        return None
    
    def get_photo_url(self):
        fname = ''
        indi_id = self.get_id()
        if MultimediaLink.objects.filter(indi=indi_id).exists():
            mml = MultimediaLink.objects.filter(indi=indi_id).order_by('_sort')[0]
            if MultimediaRecord.objects.filter(id=mml.obje.id).exists():
                mmr = MultimediaRecord.objects.filter(id=mml.obje.id).order_by('_sort')[0]
                if MultimediaFile.objects.filter(obje=mmr.id).exists():
                    mmf =  MultimediaFile.objects.filter(obje=mmr.id).order_by('_sort')[0]
                    if mmf.file:
                        fname = mmf.file.split('/')[-1]
        if fname:
            return reverse('family:doc', args=('pedigree', self.tree.id, fname))
        return ''

class PersonalNamePieces(models.Model):
    npfx = models.CharField(_('Prefix'), max_length=30, blank=True, null=True)
    givn = models.CharField(_('Given'), max_length=120, blank=True, null=True)
    nick = models.CharField(_('Nickname'), max_length=30, blank=True, null=True)
    spfx = models.CharField(_('Surname prefix'), max_length=30, blank=True, null=True)
    surn = models.CharField(_('Surname'), max_length=120, blank=True, null=True)
    nsfx = models.CharField(_('Suffix'), max_length=30, blank=True, null=True)
    _marnm = models.CharField(_('Custom field: married name'), max_length=120, blank=True, null=True)

class PersonalNameStructure(models.Model):
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('Individual'), related_name='pns_individual', null=True)
    name = models.CharField(_('Name personal'), max_length=120, blank=True, null=True)
    type = models.CharField(_('Name type'), max_length=30, blank=True, null=True)
    piec = models.ForeignKey(PersonalNamePieces, on_delete=models.SET_NULL, verbose_name=_('Pieces'), related_name='pn_pnp', null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def before_delete(self):
        for item in NamePhoneticVariation.objects.filter(name=self.id):
            item.before_delete()
        for item in NameRomanizedVariation.objects.filter(name=self.id):
            item.before_delete()
        if self.piec:
            self.piec.delete()

#--------------------------------------------------
class PlaceStructure(models.Model):
    name = models.CharField(_('Place name'), max_length=500, blank=True, null=True) # in the spec it is a recursive definition of size 120. In MyHeritage discovered 160 symbols
    map_lati = models.CharField(_('Latitude'), max_length=10, blank=True, null=True)
    map_long = models.CharField(_('Longitude'), max_length=11, blank=True, null=True)

class EventDetail(models.Model):
    type = models.CharField(_('Event or fact classification'), max_length=90, blank=True, null=True)
    date = models.CharField(_('Date value'), max_length=35, blank=True, null=True)
    plac = models.ForeignKey(PlaceStructure, on_delete=models.SET_NULL, verbose_name=_('Place'), related_name='event_place', null=True)
    addr = models.ForeignKey(AddressStructure, on_delete=models.SET_NULL, verbose_name=_('Address'), related_name='event_address', null=True)
    agnc = models.CharField(_('Responsible agency'), max_length=120, blank=True, null=True)
    reli = models.CharField(_('Religious affiliation'), max_length=90, blank=True, null=True)
    caus = models.CharField(_('Cause of event'), max_length=90, blank=True, null=True)

    def before_delete(self):
        if self.plac:
            self.plac.delete()
        if self.addr:
            self.addr.delete()

    def get_event_date(self):
        raw_date = ''
        ev_date = DateValue.parse(self.date)
        if ev_date:
            raw_date = ev_date.get_str_date()
        full = day_month = year = ''
        try:
            dt = datetime.strptime(raw_date, '%Y-%m-%d')
            full = date_format(dt, format='DATE_FORMAT', use_l10n=True)
            day_month = dt.strftime('%d %b')
            year = dt.strftime('%Y')
        except:
            try:
                year = int(raw_date)
                full = str(year)
            except:
                pass
        when = ''
        if day_month:
            when = pgettext_lazy('event date', 'on %(date)s') % {'date': full}
        elif year:
            when = pgettext_lazy('event date', 'in %(date)s') % {'date': str(year)}
        date = {
            'full': full,
            'when': when,
            'sort': raw_date,
            'day_month': day_month,
            'year': year,
        }
        return date
    
    def get_when(self):
        date = self.get_event_date()
        return date['when']

    def get_where(self):
        place = ''
        if self.plac:
            place = self.plac.name
        if place:
            place = ' ' + _('in') + ' ' + place
        return place

class NamePhoneticVariation(models.Model):
    name = models.ForeignKey(PersonalNameStructure, on_delete=models.CASCADE, verbose_name=_('Name'), related_name='name_phonetic', null=True)
    plac = models.ForeignKey(PlaceStructure, on_delete=models.CASCADE, verbose_name=_('Place'), related_name='place_phonetic', null=True)
    value = models.CharField(_('Name phonetic variation'), max_length=120, blank=True, null=True)
    type = models.CharField(_('Phonetic type'), max_length=30, blank=True, null=True)
    piec = models.ForeignKey(PersonalNamePieces, on_delete=models.SET_NULL, verbose_name=_('Pieces'), related_name='npv_piece', null=True)

    def before_delete(self):
        if self.plac:
            self.plac.delete()
        if self.piec:
            self.piec.delete()

class NameRomanizedVariation(models.Model):
    name = models.ForeignKey(PersonalNameStructure, on_delete=models.CASCADE, verbose_name=_('Name'), related_name='name_romanized', null=True)
    plac = models.ForeignKey(PlaceStructure, on_delete=models.CASCADE, verbose_name=_('Place'), related_name='place_romanized', null=True)
    value = models.CharField(_('Name romanized variation'), max_length=120, blank=True, null=True)
    type = models.CharField(_('Romanized type'), max_length=30, blank=True, null=True)
    piec = models.ForeignKey(PersonalNamePieces, on_delete=models.SET_NULL, verbose_name=_('Pieces'), related_name='nrv_piece', null=True)

    def before_delete(self):
        if self.plac:
            self.plac.delete()
        if self.piec:
            self.piec.delete()

#--------------------------------------------------
class FamRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('Tree header'), related_name='family_tree_header', null=True)
    xref = models.IntegerField(_('Identifier in the source system'), null=True)
    husb = models.ForeignKey(IndividualRecord, on_delete=models.SET_NULL, verbose_name=_('Husband'), related_name='husband', null=True)
    wife = models.ForeignKey(IndividualRecord, on_delete=models.SET_NULL, verbose_name=_('Wife'), related_name='wife', null=True)
    nchi = models.CharField(_('Number of children'), max_length=3, blank=True, null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('Change date'), related_name='family_change_date', null=True)
    _uid = models.CharField(_('Custom field: uid'), max_length=40, blank=True, null=True)
    _upd = models.CharField(_('Custom field: update'), max_length=40, blank=True, null=True)
    _mstat = models.CharField(_('Custom field: status'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def before_delete(self):
        for item in FamilyEventStructure.objects.filter(fam=self.id):
            item.before_delete()
        if self.chan:
            self.chan.delete()

    def get_id(self):
        return self.id

    def marr_date(self):
        ret = ''
        for x in FamilyEventStructure.objects.filter(fam=self.id):
            if x.tag == 'MARR' and x.deta and x.deta.date:
                try:
                    ret = datetime.strptime(str(x.deta.date), '%d %b %Y').strftime('%Y.%m.%d')
                except ValueError:
                    ret = str(x.deta.date)
        return ret
    
    def husb_name(self):
        if self.husb:
            return self.husb.name()
        return ''
    
    def wife_name(self):
        if self.wife:
            return self.wife.name()
        return ''
    
    def get_spouse(self, spouse: IndividualRecord):
        if self.husb.id == spouse.get_id():
            return self.wife
        return self.husb
    
    def get_events(self):
        return FamilyEventStructure.objects.filter(fam=self.id)

class ChildToFamilyLink(models.Model):
    fami = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('Family'), related_name='family_children')
    chil = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('Child'), related_name='family_child')
    pedi = models.CharField(_('Pedigree linkage type'), max_length=7, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

class FamilyEventStructure(models.Model):
    fam = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('Family'), related_name='event_structure_family')
    tag = models.CharField(_('Tag'), max_length=4, blank=True, null=True)
    deta = models.ForeignKey(EventDetail, on_delete=models.SET_NULL, verbose_name=_('Family event detail'), related_name='family_event_detail', null=True)
    desc = models.CharField(_('Event descriptor'), max_length=90, blank=True, null=True)
    value = models.CharField(_('Event value'), max_length=120, blank=True, null=True)
    husb_age = models.CharField(_('Husband age at event'), max_length=13, blank=True, null=True)
    wife_age = models.CharField(_('Wife age at event'), max_length=13, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def before_delete(self):
        if self.deta:
            self.deta.before_delete()
            self.deta.delete()

class IndividualEventStructure(models.Model):
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('Individual'), related_name='event_structure_individual')
    tag = models.CharField(_('Tag'), max_length=4, blank=True, null=True)
    value = models.CharField(_('Event descriptor'), max_length=500, blank=True, null=True) # max_length=90 - spec, but in MyHeritage discovered 150
    age = models.CharField(_('Age at event'), max_length=13, blank=True, null=True)
    famc = models.ForeignKey(FamRecord, on_delete=models.SET_NULL, verbose_name=_('Child'), related_name='event_structure_child', null=True)
    adop = models.CharField(_('Adopted by which parent'), max_length=4, blank=True, null=True)
    deta = models.ForeignKey(EventDetail, on_delete=models.SET_NULL, verbose_name=_('Event detail'), related_name='individual_event_event_detail', null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def before_delete(self):
        if self.deta:
            self.deta.before_delete()
            self.deta.delete()

    def get_event_date(self):
        if not self.deta:
            return None
        return self.deta.get_event_date()

    def get_when(self):
        if not self.deta:
            return ''
        return self.deta.get_when()

    def get_when_where(self):
        if not self.deta:
            return ''
        when = self.deta.get_when()
        where = self.deta.get_where()
        return when + where

class IndividualAttributeStructure(models.Model):
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('Individual'), related_name='attributes_individual', null=True)
    tag = models.CharField(_('Tag'), max_length=4, blank=True, null=True)
    value = models.CharField(_('Event descriptor'), max_length=500, blank=True, null=True) # 248 for DSCR attribute
    age = models.CharField(_('Age at event'), max_length=13, blank=True, null=True)
    type = models.CharField(_('User reference type'), max_length=40, blank=True, null=True)
    dscr = models.TextField(_('Physical description'), blank=True, null=True)
    deta = models.ForeignKey(EventDetail, on_delete=models.SET_NULL, verbose_name=_('Event detail'), related_name='individual_attr_event_detail', null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def before_delete(self):
        if self.deta:
            self.deta.before_delete()
            self.deta.delete()

class AssociationStructure(models.Model):
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('Individual'), related_name='association_individual', null=True)
    asso = models.CharField(_('Identifier in the source system'), max_length=22, blank=True, null=True)
    asso_rela = models.CharField(_('Relation is descriptor'), max_length=25, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

class NoteRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('Tree header'), related_name='note_tree_header', null=True)
    xref = models.IntegerField(_('Identifier in the source system'), null=True)
    note = models.TextField(_('Description'), blank=True, null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('Change date'), related_name='note_change_date', null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def before_delete(self):
        if self.chan:
            self.chan.delete()

class RepositoryRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('Tree header'), related_name='repo_tree_header', null=True)
    xref = models.IntegerField(_('Identifier in the source system'), null=True)
    name = models.CharField(_('Name of repository'), max_length=57, blank=True, null=True)
    addr = models.ForeignKey(AddressStructure, on_delete=models.SET_NULL, verbose_name=_('Address'), related_name='repository_address', null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('Change date'), related_name='repo_change_date', null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def before_delete(self):
        if self.addr:
            self.addr.delete()
        if self.chan:
            self.chan.delete()

class SourceRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('Tree header'), related_name='source_tree_header', null=True)
    xref = models.IntegerField(_('Identifier in the source system'), null=True)
    data_even = models.CharField(_('Events recorded'), max_length=90, blank=True, null=True)
    data_date = models.CharField(_('Date period'), max_length=35, blank=True, null=True)
    data_plac = models.CharField(_('Source jurisdiction place'), max_length=120, blank=True, null=True)
    data_agnc = models.CharField(_('Responsible agency'), max_length=120, blank=True, null=True)
    auth = models.TextField(_('Source originator'), blank=True, null=True)
    titl = models.TextField(_('Source descriptive title'), blank=True, null=True)
    abbr = models.CharField(_('Source field by entry'), max_length=60, blank=True, null=True)
    publ = models.TextField(_('Source publication facts'), blank=True, null=True)
    text = models.TextField(_('Text from source'), blank=True, null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('Change date'), related_name='source_change_date', null=True)
    _upd = models.CharField(_('Custom field: update'), max_length=40, blank=True, null=True)
    _type = models.CharField(_('Custom field: type'), max_length=40, blank=True, null=True)
    _medi = models.CharField(_('Custom field: media id'), max_length=40, blank=True, null=True)
    _uid = models.CharField(_('Custom field: uid'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def before_delete(self):
        if self.chan:
            self.chan.delete()

class SourceRepositoryCitation(models.Model):
    repo = models.ForeignKey(RepositoryRecord, on_delete=models.CASCADE, verbose_name=_('Citation repository'), related_name='citation_repository', null=True)
    sour = models.ForeignKey(SourceRecord, on_delete=models.CASCADE, verbose_name=_('Citation source'), related_name='citation_source', null=True)
    caln = models.CharField(_('Source call number'), max_length=120, blank=True, null=True)
    caln_medi = models.CharField(_('Source media type'), max_length=15, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

class SubmitterRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('Tree header'), related_name='submitter_tree_header', null=True)
    xref = models.IntegerField(_('Identifier in the source system'), null=True)
    name = models.CharField(_('Submitter name'), max_length=60, blank=True, null=True)
    addr = models.ForeignKey(AddressStructure, on_delete=models.SET_NULL, verbose_name=_('Address'), related_name='submitter_address', null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('Change date'), related_name='submitter_change_date', null=True)
    _uid = models.CharField(_('Custom field: uid'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def before_delete(self):
        if self.addr:
            self.addr.delete()
        if self.chan:
            self.chan.delete()

#--------------------------------------------------
class AlbumRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('Tree header'), related_name='album_tree_header', null=True)
    xref = models.IntegerField(_('Identifier in the source system'), null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('Change date'), related_name='album_change_date', null=True)
    titl = models.CharField(_('Title'), max_length=250, blank=True, null=True)
    desc = models.CharField(_('Title'), max_length=250, blank=True, null=True)
    _upd = models.CharField(_('Custom field: update'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def before_delete(self):
        if self.chan:
            self.chan.delete()

#--------------------------------------------------
class MultimediaRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('Tree header'), related_name='mm_tree_header', null=True)
    xref = models.IntegerField(_('Identifier in the source system'), null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('Change date'), related_name='mfile_change_date', null=True)
    _size = models.CharField(_('Custom field: file size'), max_length=15, blank=True, null=True)
    _date = models.CharField(_('Custom field: date'), max_length=15, blank=True, null=True)
    _plac = models.CharField(_('Custom field: place'), max_length=250, blank=True, null=True)
    _prim = models.CharField(_('Custom field: prim'), max_length=1, blank=True, null=True)
    _cuto = models.CharField(_('Custom field: cutout'), max_length=1, blank=True, null=True)
    _pari = models.CharField(_('Custom field: parent rin'), max_length=100, blank=True, null=True)
    _pers = models.CharField(_('Custom field: personal photo'), max_length=1, blank=True, null=True)
    _prcu = models.CharField(_('Custom field: prim cutout'), max_length=1, blank=True, null=True)
    _pare = models.CharField(_('Custom field: parent photo'), max_length=1, blank=True, null=True)
    _prin = models.CharField(_('Custom field: parent RIN'), max_length=12, blank=True, null=True)
    _posi = models.CharField(_('Custom field: position'), max_length=50, blank=True, null=True)
    _albu = models.ForeignKey(AlbumRecord, on_delete=models.SET_NULL, verbose_name=_('Album'), related_name='mfile_album', null=True)
    _uid = models.CharField(_('Custom field: uid'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

    def before_delete(self):
        if self.chan:
            self.chan.delete()

    def get_info(self):
        ret = ''
        if MultimediaFile.objects.filter(obje=self.id).exists():
            file = MultimediaFile.objects.filter(obje=self.id)[0]
            if file.file:
                ret = file.file.split('/')[-1:][0][:30]
            if file.titl:
                if ret:
                    ret += ' '
                ret += file.titl[:70]
        return ret

    def get_file(self):
        if MultimediaFile.objects.filter(obje=self.id).exists():
            mmf = MultimediaFile.objects.filter(obje=self.id)[0]
            if mmf.file:
                return mmf.file.split('/')[-1]
        return None

    def get_format(self):
        if MultimediaFile.objects.filter(obje=self.id).exists():
            mmf = MultimediaFile.objects.filter(obje=self.id)[0]
            return mmf.form.lower().replace('jpg', 'jpeg')
        return None

class MultimediaFile(models.Model):
    obje = models.ForeignKey(MultimediaRecord, on_delete=models.CASCADE, verbose_name=_('Multimedia record'), related_name='multimedia_record_file', null=True)
    file = models.CharField(_('Multimedia file reference'), max_length=259, blank=True, null=True)
    form = models.CharField(_('Multimedia format'), max_length=4, blank=True, null=True)
    type = models.CharField(_('Source media type'), max_length=15, blank=True, null=True)
    medi = models.CharField(_('Source media type'), max_length=15, blank=True, null=True)
    titl = models.CharField(_('Descriptive title'), max_length=248, blank=True, null=True)
    _fdte = models.CharField(_('Custom field: fdte'), max_length=50, blank=True, null=True)
    _fplc = models.CharField(_('Custom field: fplc'), max_length=250, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

#--------------------------------------------------
class SourceCitation(models.Model):
    fam = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('Family'), related_name='source_citation_family', null=True)
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('Individual'), related_name='source_citation_individual', null=True)
    asso = models.ForeignKey(AssociationStructure, on_delete=models.CASCADE, verbose_name=_('Association'), related_name='source_citation_association', null=True)
    obje = models.ForeignKey(MultimediaRecord, on_delete=models.CASCADE, verbose_name=_('Multimedia'), related_name='source_citation_multimedia', null=True)
    even = models.ForeignKey(EventDetail, on_delete=models.CASCADE, verbose_name=_('Event detail'), related_name='source_citation_event_detail', null=True)
    pnpi = models.ForeignKey(PersonalNamePieces, on_delete=models.CASCADE, verbose_name=_('Personal name pieces'), related_name='source_citation_personal_name_pieces', null=True)
    note = models.ForeignKey(NoteRecord, on_delete=models.CASCADE, verbose_name=_('Note'), related_name='source_citation_note', null=True)
    sour = models.ForeignKey(SourceRecord, on_delete=models.CASCADE, verbose_name=_('Source'), related_name='source_citation_source', null=True)
    page = models.CharField(_('Where within source'), max_length=248, blank=True, null=True)
    even_even = models.CharField(_('Event type cited from'), max_length=15, blank=True, null=True)
    even_role = models.CharField(_('Role in event'), max_length=27, blank=True, null=True)
    data_date = models.CharField(_('Entry recording date'), max_length=90, blank=True, null=True)
    data_text = models.TextField(_('Text from source'), blank=True, null=True)
    quay = models.CharField(_('Certainty assessment'), max_length=1, blank=True, null=True)
    auth = models.CharField(_('Author'), max_length=120, blank=True, null=True)
    titl = models.CharField(_('Title'), max_length=250, blank=True, null=True)
    _upd = models.CharField(_('Custom field: update'), max_length=40, blank=True, null=True)
    _type = models.CharField(_('Custom field: type'), max_length=40, blank=True, null=True)
    _medi = models.CharField(_('Custom field: media id'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

class FamilySourceCitation(models.Model):
    fami = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('Family'), related_name='family_source_citation_family')
    soci = models.ForeignKey(SourceCitation, on_delete=models.CASCADE, verbose_name=_('Source citation'), related_name='family_source_citation')

#--------------------------------------------------
class MultimediaLink(models.Model):
    obje = models.ForeignKey(MultimediaRecord, on_delete=models.CASCADE, verbose_name=_('Multimedia'), related_name='multimedia_link', null=True)
    fam = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('Family'), related_name='family_mm_link', null=True)
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('Individual'), related_name='individual_mm_link', null=True)
    cita = models.ForeignKey(SourceCitation, on_delete=models.CASCADE, verbose_name=_('Source citation'), related_name='source_citation_mm_link', null=True)
    sour = models.ForeignKey(SourceRecord, on_delete=models.CASCADE, verbose_name=_('Source'), related_name='source_mm_link', null=True)
    subm = models.ForeignKey(SubmitterRecord, on_delete=models.CASCADE, verbose_name=_('Submitter'), related_name='submitter_mm_link', null=True)
    even = models.ForeignKey(EventDetail, on_delete=models.CASCADE, verbose_name=_('Event detail'), related_name='event_detail_mm_link', null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

#--------------------------------------------------
class NoteStructure(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('Gedcom content description'), related_name='note_structure_tree_note', null=True)
    fam = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('Family'), related_name='family_note', null=True)
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('Individual'), related_name='individual_note', null=True)
    cita = models.ForeignKey(SourceCitation, on_delete=models.CASCADE, verbose_name=_('Source citation'), related_name='source_citation_note', null=True)
    asso = models.ForeignKey(AssociationStructure, on_delete=models.CASCADE, verbose_name=_('Association'), related_name='association_note', null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.CASCADE, verbose_name=_('Change date'), related_name='change_date_note', null=True)
    famc = models.ForeignKey(ChildToFamilyLink, on_delete=models.CASCADE, verbose_name=_('Child to family link'), related_name='ctfl_date_note', null=True)
    obje = models.ForeignKey(MultimediaRecord, on_delete=models.CASCADE, verbose_name=_('Multimedia'), related_name='multimedia_note', null=True)
    repo = models.ForeignKey(RepositoryRecord, on_delete=models.CASCADE, verbose_name=_('Repository'), related_name='repository_note', null=True)
    sour = models.ForeignKey(SourceRecord, on_delete=models.CASCADE, verbose_name=_('Source'), related_name='source_note', null=True)
    srci = models.ForeignKey(SourceRepositoryCitation, on_delete=models.CASCADE, verbose_name=_('Source repository citation'), related_name='source_repository_citation_note', null=True)
    subm = models.ForeignKey(SubmitterRecord, on_delete=models.CASCADE, verbose_name=_('Submitter'), related_name='submitter_note', null=True)
    even = models.ForeignKey(EventDetail, on_delete=models.CASCADE, verbose_name=_('Event detail'), related_name='event_detail_note', null=True)
    pnpi = models.ForeignKey(PersonalNamePieces, on_delete=models.CASCADE, verbose_name=_('Personal name pieces'), related_name='personal_name_pieces_note', null=True)
    plac = models.ForeignKey(PlaceStructure, on_delete=models.CASCADE, verbose_name=_('Place'), related_name='place_note', null=True)
    note = models.ForeignKey(NoteRecord, on_delete=models.CASCADE, verbose_name=_('Note'), related_name='note_structure_note', null=True)
    mode = models.IntegerField(_('Which part of noted structure'), default=0)
    _sort = models.IntegerField(_('Sort order'), null=True)

class UserReferenceNumber(models.Model):
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('Individual'), related_name='individual_refn', null=True)
    fam  = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('Family'), related_name='family_refn', null=True)
    obje = models.ForeignKey(MultimediaRecord, on_delete=models.CASCADE, verbose_name=_('Multimedia record'), related_name='multimedia_record_refn', null=True)
    note = models.ForeignKey(NoteRecord, on_delete=models.CASCADE, verbose_name=_('Note'), related_name='note_refn')
    repo = models.ForeignKey(RepositoryRecord, on_delete=models.CASCADE, verbose_name=_('Repository'), related_name='repository_refn', null=True)
    sour = models.ForeignKey(SourceRecord, on_delete=models.CASCADE, verbose_name=_('Source'), related_name='source_refn', null=True)
    refn = models.CharField(_('User reference number'), max_length=20, blank=True, null=True)
    type = models.CharField(_('User reference type'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('Sort order'), null=True)

class Params(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name = 'genealogy_user')
    cur_tree = models.ForeignKey(FamTree, on_delete=models.SET_NULL, verbose_name=_('current tree'), related_name='users_current_tree', null=True)

    @classmethod
    def get_cur_tree(cls, user) -> FamTree:
        if Params.objects.filter(user=user.id).exists():
            params = Params.objects.filter(user=user.id).get()
            if params.cur_tree:
                if FamTreeUser.objects.filter(user_id=user.id, tree_id=params.cur_tree.id).exists():
                    return params.cur_tree
                params.cur_tree = None
                params.save()
        if len(FamTreeUser.objects.filter(user_id=user.id)) > 0:
            user_tree = FamTreeUser.objects.filter(user_id=user.id).order_by('sort')[0]
            tree = FamTree.objects.filter(id=user_tree.tree_id).get()
            Params.set_cur_tree(user, tree)
            return tree
        return None

    @classmethod
    def set_cur_tree(cls, user, tree: FamTree):
        if user and tree:
            if not Params.objects.filter(user=user.id).exists():
                Params.objects.create(user=user, cur_tree=tree)
            else:
                params = Params.objects.filter(user=user.id).get()
                params.cur_tree = tree
                params.save()

class UserSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'settings_user')
    tree = models.ForeignKey(FamTree, on_delete=models.SET_NULL, verbose_name='Family tree', related_name='users_tree', null=True)
    indi_self = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('User in the tree'), related_name='individual_self', null=True)
    indi_sel = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('Selected person'), related_name='individual_selected', null=True)

    @classmethod
    def get_sel_indi(cls, user, tree):
        if tree and FamTreeUser.objects.filter(user_id=user.id, tree_id=tree.id).exists():
            if not UserSettings.objects.filter(user=user.id, tree=tree.id).exists():
                if IndividualRecord.objects.filter(tree=tree.id).exists():
                    indi = IndividualRecord.objects.filter(tree=tree.id)[0]
                    cls.set_sel_indi(user, tree, None)
                    return indi
            else:
                us = UserSettings.objects.filter(user=user.id, tree=tree.id).get()
                if us.indi_sel:
                    return us.indi_sel
                if IndividualRecord.objects.filter(tree=tree.id).exists():
                    indi = IndividualRecord.objects.filter(tree=tree.id)[0]
                    cls.set_sel_indi(user, tree, None)
                    return indi
        return None
            
    @classmethod
    def set_sel_indi(cls, user, tree, indi):
        if user and tree and indi:
            if not UserSettings.objects.filter(user=user.id, tree=tree.id).exists():
                UserSettings.objects.create(user=user, tree=tree, indi_sel=indi)
            else:
                us = UserSettings.objects.filter(user=user.id, tree=tree.id).get()
                us.indi_sel = indi
                us.save()

#####################################################################################################
# Views
#             

class Gedcom(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('Family tree'), related_name='gedcom_tree')
    row_num = models.IntegerField('Row number', null=False)
    value = models.CharField('Row walue', max_length=500, blank=False, null=False)
    used_by_chart = models.BooleanField('Used by chart', default=True)
