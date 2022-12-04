from datetime import datetime
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from family.const import *

#--------------------------------------------------
class AddressStructure(models.Model):
    addr = models.CharField(_('address value'), max_length=500, blank=True, null=True)
    addr_adr1 = models.CharField(_('address line 1'), max_length=60, blank=True, null=True)
    addr_adr2 = models.CharField(_('address line 2'), max_length=60, blank=True, null=True)
    addr_adr3 = models.CharField(_('address line 3'), max_length=60, blank=True, null=True)
    addr_city = models.CharField(_('city'), max_length=60, blank=True, null=True)
    addr_stae = models.CharField(_('state'), max_length=60, blank=True, null=True)
    addr_post = models.CharField(_('postal code'), max_length=10, blank=True, null=True)
    addr_ctry = models.CharField(_('country'), max_length=60, blank=True, null=True)
    phon = models.CharField(_('phone number'), max_length=25, blank=True, null=True)
    phon2 = models.CharField(_('phone number 2'), max_length=25, blank=True, null=True)
    phon3 = models.CharField(_('phone number 3'), max_length=25, blank=True, null=True)
    email = models.CharField(_('email'), max_length=120, blank=True, null=True)
    email2 = models.CharField(_('email 2'), max_length=120, blank=True, null=True)
    email3 = models.CharField(_('email 3'), max_length=120, blank=True, null=True)
    fax = models.CharField(_('fax'), max_length=60, blank=True, null=True)
    fax2 = models.CharField(_('fax 2'), max_length=60, blank=True, null=True)
    fax3 = models.CharField(_('fax 3'), max_length=60, blank=True, null=True)
    www = models.CharField(_('web page'), max_length=2047, blank=True, null=True)
    www2 = models.CharField(_('web page 2'), max_length=2047, blank=True, null=True)
    www3 = models.CharField(_('web page 3'), max_length=2047, blank=True, null=True)
    owner = models.CharField(_('owner of this record'), max_length=20, blank=True, null=True)

class ChangeDate(models.Model):
    date_time = models.DateTimeField(_('change date-time'), blank=True, null=True)
    date = models.CharField(_('date'), max_length=20, blank=True, null=True)
    time = models.CharField(_('time'), max_length=20, blank=True, null=True)
    owner = models.CharField(_('owner of this record'), max_length=20, blank=True, null=True)

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
    sour = models.CharField(_('system ID'), max_length=50, blank=True, null=True)
    sour_vers = models.CharField(_('version number'), max_length=15, blank=True, null=True)
    sour_name = models.CharField(_('name of product'), max_length=90, blank=True, null=True)
    sour_corp = models.CharField(_('name of business'), max_length=90, blank=True, null=True)
    sour_corp_addr = models.ForeignKey(AddressStructure, on_delete=models.SET_NULL, verbose_name=_('business address'), related_name='business_address', null=True)
    sour_data = models.CharField(_('name of source data'), max_length=90, blank=True, null=True)
    sour_data_date = models.DateField(_('publication date'), blank=True, null=True)
    sour_data_copr = models.TextField(_('copyright source data'), blank=True, null=True)
    dest = models.CharField(_('receiving system name'), max_length=20, blank=True, null=True)
    date = models.CharField(_('transmission date'), max_length=11, blank=True, null=True)
    time = models.CharField(_('time value'), max_length=12, blank=True, null=True)
    subm_id = models.IntegerField(_('submitter reference'), blank=True, null=True)
    file = models.CharField(_('file name'), max_length=90, blank=True, null=True)
    copr = models.CharField(_('copyright gedcom file'), max_length=90, blank=True, null=True)
    gedc_vers = models.CharField(_('gedcom version number'), max_length=15, blank=True, null=True)
    gedc_form = models.CharField(_('gedcom form'), max_length=20, blank=True, null=True)
    gedc_form_vers = models.CharField(_('gedcom formversion number'), max_length=15, blank=True, null=True)
    char = models.CharField(_('character set'), max_length=12, blank=True, null=True)
    lang = models.CharField(_('language of text'), max_length=15, blank=True, null=True)
    note = models.TextField(_('gedcom content description'), blank=True, null=True)
    mh_id = models.CharField(_('ID in MyHeritage.com'), max_length=50, blank=True, null=True)
    mh_prj_id = models.CharField(_('project GUID'), max_length=200, blank=True, null=True)
    mh_rtl = models.CharField(_('source RTL'), max_length=200, blank=True, null=True)
    sort = models.IntegerField(_('sorting position'), null=True)
    created = models.DateTimeField(_('creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)
    mark = models.CharField(_('debug marker'), max_length=20, blank=True, null=True)
    cur_indi = models.IntegerField(_('current individual id'), null=True)
    name = models.CharField(_('family tree name'), max_length=200, blank=True, null=True)
    depth = models.IntegerField(_('tree depth'), default=0, null=True)

    def __str__(self):
        return self.name

    def s_id(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('family:famtree-details', args=(self.id,))

    def before_delete(self):
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

    def is_leaf(self):
        return True

    def store_name(self):
        name = self.name
        if not name:
            pos = self.file.rfind('.')
            if pos:
                name = self.file[:pos]
            else:
                name = self.file
        return name

#--------------------------------------------------
class IndividualRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('tree header'), related_name='individual_tree_header', null=True)
    xref = models.IntegerField(_('identifier in the source system'), null=True)
    sex = models.CharField(_('sex'), max_length=1, blank=True, null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('change_date'), related_name='individual_change_date', null=True)
    _upd = models.CharField(_('custom field: update'), max_length=40, blank=True, null=True)
    _uid = models.CharField(_('custom field: uid'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

    def __str__(self):
        return self.name()

    def before_delete(self):
        for item in IndividualEventStructure.objects.filter(indi=self.id):
            item.before_delete()
        for item in IndividualAttributeStructure.objects.filter(indi=self.id):
            item.before_delete()
        for item in PersonalNameStructure.objects.filter(indi=self.id):
            item.before_delete()
        if self.chan:
            self.chan.delete()

    def name(self):
        ret = ''
        if PersonalNameStructure.objects.filter(indi=self.id).exists():
            pns = PersonalNameStructure.objects.filter(indi=self.id)[0]
            if pns.piec:
                if pns.piec.surn:
                    ret = pns.piec.surn
                if pns.piec.givn:
                    if ret:
                        ret += ' '
                    ret += pns.piec.givn
        return ret

    def short_name(self):
        ret = self.name()
        if len(ret) > 16:
            ret = ret[:16] + '...'
        return ret

    def dates(self):
        ret = ''
        birth = self.born()
        death = self.died()
        if birth:
            ret = birth
            if death:
                ret += ' - ' + death
            else:
                ret += ' -'
        else:
            if death:
                ret = '- ' + death
            else:
                ret = 'N/A'
        return ret

    def born(self):
        ret = ''
        for x in IndividualEventStructure.objects.filter(indi=self.id):
            if x.tag == 'BIRT' and x.deta and x.deta.date:
                try:
                    ret = datetime.strptime(str(x.deta.date), '%d %b %Y').strftime('%Y.%m.%d')
                except ValueError:
                    ret = str(x.deta.date)
        return ret

    def died(self):
        ret = ''
        for x in IndividualEventStructure.objects.filter(indi=self.id):
            if x.tag == 'DEAT' and x.deta and x.deta.date:
                try:
                    ret = datetime.strptime(str(x.deta.date), '%d %b %Y').strftime('%Y.%m.%d')
                except ValueError:
                    ret = str(x.deta.date)
        return ret

    def has_fam(self):
        fams = ChildToFamilyLink.objects.filter(chil=self.id)
        return (len(fams) > 0)

    def get_fam(self):
        fams = ChildToFamilyLink.objects.filter(chil=self.id)
        if len(fams):
            return fams[0].fami
        return None

    def get_children(self):
        ret = []
        if self.sex == 'M':
            for f in FamRecord.objects.filter(husb=self.id):
                for ctfl in ChildToFamilyLink.objects.filter(fami=f):
                    ret.append(ctfl.chil)
        if self.sex == 'F':
            for f in FamRecord.objects.filter(wife=self.id):
                for ctfl in ChildToFamilyLink.objects.filter(fami=f):
                    ret.append(ctfl.chil)
        return sorted(ret, key=lambda x: x.born())

    def photo(self):
        photo = ''
        for ml in MultimediaLink.objects.filter(indi=self.id):
            if (ml.obje._prim == 'Y'):
                if (ml.obje._cuto == 'Y' and ml.obje._pari and MultimediaRecord.objects.filter(tree=self.tree.id, _prin=ml.obje._pari).exists()):
                    mr = MultimediaRecord.objects.filter(tree=self.tree.id, _prin=ml.obje._pari)[0]
                    mf = MultimediaFile.objects.filter(obje=mr.id)[0]
                else:
                    mf = MultimediaFile.objects.filter(obje=ml.obje.id)[0]
                if mf.file:
                    photo = mf.file.split('/')[-1]
                    break
        if not photo:
            if MultimediaLink.objects.filter(indi=self.id).exists():
                ml = MultimediaLink.objects.filter(indi=self.id)[0]
                if MultimediaFile.objects.filter(obje=ml.obje.id).exists():
                    mf = MultimediaFile.objects.filter(obje=ml.obje.id)[0]
                    if mf.file:
                        photo = mf.file.split('/')[-1]
        if photo:
            return reverse('family:photo', args=(self.tree.id,)) + '?file=' + photo
        if self.sex == 'M':
            return '/static/img/man.jpg'
        return '/static/img/woman.jpg'

    def prim_mmr(self):
        mmr = None
        for mml in MultimediaLink.objects.filter(indi=self.id):
            if (mml.obje._prim == 'Y'):
                if (mml.obje._cuto == 'Y' and mml.obje._pari and MultimediaRecord.objects.filter(tree=self.tree.id, _prin=mml.obje._pari).exists()):
                    mmr = MultimediaRecord.objects.filter(tree=self.tree.id, _prin=mml.obje._pari)[0]
                    break
        if not mmr:
            if MultimediaLink.objects.filter(indi=self.id).exists():
                mmr = MultimediaLink.objects.filter(indi=self.id)[0].obje
        if mmr:
            return reverse('family:thumbnail', args=(self.tree.id,)) + '?mmr=' + str(mmr.id)
        if self.sex == 'M':
            return '/static/img/man.jpg'
        return '/static/img/woman.jpg'
    
    def get_avatar_mmr(self):
        mmr = None
        for mml in MultimediaLink.objects.filter(indi=self.id):
            if (mml.obje._prim == 'Y'):
                if (mml.obje._cuto == 'Y' and mml.obje._pari and MultimediaRecord.objects.filter(tree=self.tree.id, _prin=mml.obje._pari).exists()):
                    mmr = MultimediaRecord.objects.filter(tree=self.tree.id, _prin=mml.obje._pari)[0]
        if not mmr:
            if MultimediaLink.objects.filter(indi=self.id).exists():
                mmr = MultimediaLink.objects.filter(indi=self.id)[0].obje
        return mmr
    
    def prefix(self):
        ret = ''
        if PersonalNameStructure.objects.filter(indi=self.id).exists():
            pns = PersonalNameStructure.objects.filter(indi=self.id)[0]
            if pns.piec:
                if pns.piec.npfx:
                    ret = pns.piec.npfx
        return ret

    def names(self):
        ret = ''
        if PersonalNameStructure.objects.filter(indi=self.id).exists():
            pns = PersonalNameStructure.objects.filter(indi=self.id)[0]
            if pns.piec:
                if pns.piec.givn:
                    ret = pns.piec.givn
        return ret

    def last_name(self):
        ret = ''
        if PersonalNameStructure.objects.filter(indi=self.id).exists():
            pns = PersonalNameStructure.objects.filter(indi=self.id)[0]
            if pns.piec:
                if pns.piec.surn:
                    ret = pns.piec.surn
        return ret

    def prefix(self):
        ret = ''
        if PersonalNameStructure.objects.filter(indi=self.id).exists():
            pns = PersonalNameStructure.objects.filter(indi=self.id)[0]
            if pns.piec:
                if pns.piec.nsfx:
                    ret = pns.piec.nsfx
        return ret

    def age(self):
        birt = None
        birt_year = None
        deat = None
        deat_year = None
        for x in IndividualEventStructure.objects.filter(indi=self.id):
            if x.tag == 'BIRT' and x.deta and x.deta.date:
                try:
                    birt = datetime.strptime(str(x.deta.date), '%d %b %Y')
                except ValueError:
                    try:
                        birt_year = int(str(x.deta.date))
                    except ValueError:
                        pass
                if birt:
                    birt_year = birt.year
            if x.tag == 'DEAT' and x.deta and x.deta.date:
                try:
                    deat = datetime.strptime(str(x.deta.date), '%d %b %Y')
                except ValueError:
                    try:
                        deat_year = int(str(x.deta.date))
                    except ValueError:
                        pass
                if deat:
                    deat_year = deat.year
        if not birt_year:
            return ''
        if not deat_year:
            today = datetime.today()
            years = today.year - birt_year
            if birt:
                if today.month < birt.month or (today.month == birt.month and today.day < birt.day):
                    years -= 1
            return str(years)
        else:
            years = deat_year - birt_year
            if birt and deat:
                if deat.month < birt.month or (deat.month == birt.month and deat.day < birt.day):
                    years -= 1
            return str(years)

    def get_absolute_url(self):
        return reverse('family:list') + '?indi=' + str(self.id)

class PersonalNamePieces(models.Model):
    npfx = models.CharField(_('prefix'), max_length=30, blank=True, null=True)
    givn = models.CharField(_('given'), max_length=120, blank=True, null=True)
    nick = models.CharField(_('nickname'), max_length=30, blank=True, null=True)
    spfx = models.CharField(_('surname prefix'), max_length=30, blank=True, null=True)
    surn = models.CharField(_('surname'), max_length=120, blank=True, null=True)
    nsfx = models.CharField(_('suffix'), max_length=30, blank=True, null=True)
    _marnm = models.CharField(_('custom field: married name'), max_length=120, blank=True, null=True)

class PersonalNameStructure(models.Model):
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('individual'), related_name='pns_individual', null=True)
    name = models.CharField(_('name personal'), max_length=120, blank=True, null=True)
    type = models.CharField(_('name type'), max_length=30, blank=True, null=True)
    piec = models.ForeignKey(PersonalNamePieces, on_delete=models.SET_NULL, verbose_name=_('pieces'), related_name='pn_pnp', null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

    def before_delete(self):
        for item in NamePhoneticVariation.objects.filter(name=self.id):
            item.before_delete()
        for item in NameRomanizedVariation.objects.filter(name=self.id):
            item.before_delete()
        if self.piec:
            self.piec.delete()

#--------------------------------------------------
class PlaceStructure(models.Model):
    name = models.CharField(_('place name'), max_length=120, blank=True, null=True)
    map_lati = models.CharField(_('latitude'), max_length=10, blank=True, null=True)
    map_long = models.CharField(_('longitude'), max_length=11, blank=True, null=True)

class EventDetail(models.Model):
    type = models.CharField(_('event or fact classification'), max_length=90, blank=True, null=True)
    date = models.CharField(_('date value'), max_length=35, blank=True, null=True)
    plac = models.ForeignKey(PlaceStructure, on_delete=models.SET_NULL, verbose_name=_('place'), related_name='event_place', null=True)
    addr = models.ForeignKey(AddressStructure, on_delete=models.SET_NULL, verbose_name=_('address'), related_name='event_address', null=True)
    agnc = models.CharField(_('responsible agency'), max_length=120, blank=True, null=True)
    reli = models.CharField(_('religious affiliation'), max_length=90, blank=True, null=True)
    caus = models.CharField(_('cause of event'), max_length=90, blank=True, null=True)

    def before_delete(self):
        if self.plac:
            self.plac.delete()
        if self.addr:
            self.addr.delete()

class NamePhoneticVariation(models.Model):
    name = models.ForeignKey(PersonalNameStructure, on_delete=models.CASCADE, verbose_name=_('name'), related_name='name_phonetic', null=True)
    plac = models.ForeignKey(PlaceStructure, on_delete=models.CASCADE, verbose_name=_('place'), related_name='place_phonetic', null=True)
    value = models.CharField(_('name phonetic variation'), max_length=120, blank=True, null=True)
    type = models.CharField(_('phonetic type'), max_length=30, blank=True, null=True)
    piec = models.ForeignKey(PersonalNamePieces, on_delete=models.SET_NULL, verbose_name=_('pieces'), related_name='npv_piece', null=True)

    def before_delete(self):
        if self.plac:
            self.plac.delete()
        if self.piec:
            self.piec.delete()

class NameRomanizedVariation(models.Model):
    name = models.ForeignKey(PersonalNameStructure, on_delete=models.CASCADE, verbose_name=_('name'), related_name='name_romanized', null=True)
    plac = models.ForeignKey(PlaceStructure, on_delete=models.CASCADE, verbose_name=_('place'), related_name='place_romanized', null=True)
    value = models.CharField(_('name romanized variation'), max_length=120, blank=True, null=True)
    type = models.CharField(_('romanized type'), max_length=30, blank=True, null=True)
    piec = models.ForeignKey(PersonalNamePieces, on_delete=models.SET_NULL, verbose_name=_('pieces'), related_name='nrv_piece', null=True)

    def before_delete(self):
        if self.plac:
            self.plac.delete()
        if self.piec:
            self.piec.delete()

#--------------------------------------------------
class FamRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('tree header'), related_name='family_tree_header', null=True)
    xref = models.IntegerField(_('identifier in the source system'), null=True)
    husb = models.ForeignKey(IndividualRecord, on_delete=models.SET_NULL, verbose_name=_('husband'), related_name='husband', null=True)
    wife = models.ForeignKey(IndividualRecord, on_delete=models.SET_NULL, verbose_name=_('wife'), related_name='wife', null=True)
    nchi = models.CharField(_('number of children'), max_length=3, blank=True, null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('change_date'), related_name='family_change_date', null=True)
    _uid = models.CharField(_('custom field: uid'), max_length=40, blank=True, null=True)
    _upd = models.CharField(_('custom field: update'), max_length=40, blank=True, null=True)
    _mstat = models.CharField(_('custom field: status'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

    def before_delete(self):
        for item in FamilyEventStructure.objects.filter(fam=self.id):
            item.before_delete()
        if self.chan:
            self.chan.delete()

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

class ChildToFamilyLink(models.Model):
    fami = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('family'), related_name='family_children')
    chil = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('child'), related_name='family_child')
    pedi = models.CharField(_('pedigree linkage type'), max_length=7, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

class FamilyEventStructure(models.Model):
    fam = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('family'), related_name='event_structure_family')
    tag = models.CharField(_('tag'), max_length=4, blank=True, null=True)
    deta = models.ForeignKey(EventDetail, on_delete=models.SET_NULL, verbose_name=_('family event detail'), related_name='family_event_detail', null=True)
    desc = models.CharField(_('event descriptor'), max_length=90, blank=True, null=True)
    value = models.CharField(_('event value'), max_length=120, blank=True, null=True)
    husb_age = models.CharField(_('husband age at event'), max_length=13, blank=True, null=True)
    wife_age = models.CharField(_('wife age at event'), max_length=13, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

    def before_delete(self):
        if self.deta:
            self.deta.before_delete()
            self.deta.delete()

class IndividualEventStructure(models.Model):
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('individual'), related_name='event_structure_individual')
    tag = models.CharField(_('tag'), max_length=4, blank=True, null=True)
    value = models.CharField(_('event descriptor'), max_length=90, blank=True, null=True)
    age = models.CharField(_('age at event'), max_length=13, blank=True, null=True)
    famc = models.ForeignKey(FamRecord, on_delete=models.SET_NULL, verbose_name=_('child'), related_name='event_structure_child', null=True)
    adop = models.CharField(_('adopted by which parent'), max_length=4, blank=True, null=True)
    deta = models.ForeignKey(EventDetail, on_delete=models.SET_NULL, verbose_name=_('event_detail'), related_name='individual_event_event_detail', null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

    def before_delete(self):
        if self.deta:
            self.deta.before_delete()
            self.deta.delete()

class IndividualAttributeStructure(models.Model):
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('individual'), related_name='attributes_individual', null=True)
    tag = models.CharField(_('tag'), max_length=4, blank=True, null=True)
    value = models.CharField(_('event descriptor'), max_length=90, blank=True, null=True)
    age = models.CharField(_('age at event'), max_length=13, blank=True, null=True)
    type = models.CharField(_('user reference type'), max_length=40, blank=True, null=True)
    dscr = models.TextField(_('physical description'), blank=True, null=True)
    deta = models.ForeignKey(EventDetail, on_delete=models.SET_NULL, verbose_name=_('event_detail'), related_name='individual_attr_event_detail', null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

    def before_delete(self):
        if self.deta:
            self.deta.before_delete()
            self.deta.delete()

class AssociationStructure(models.Model):
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('individual'), related_name='association_individual', null=True)
    asso = models.CharField(_('identifier in the source system'), max_length=22, blank=True, null=True)
    asso_rela = models.CharField(_('relation is descriptor'), max_length=25, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

class NoteRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('tree header'), related_name='note_tree_header', null=True)
    xref = models.IntegerField(_('identifier in the source system'), null=True)
    note = models.TextField(_('description'), blank=True, null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('change_date'), related_name='note_change_date', null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

    def before_delete(self):
        if self.chan:
            self.chan.delete()

class RepositoryRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('tree header'), related_name='repo_tree_header', null=True)
    xref = models.IntegerField(_('identifier in the source system'), null=True)
    name = models.CharField(_('name of repository'), max_length=57, blank=True, null=True)
    addr = models.ForeignKey(AddressStructure, on_delete=models.SET_NULL, verbose_name=_('address'), related_name='repository_address', null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('change_date'), related_name='repo_change_date', null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

    def before_delete(self):
        if self.addr:
            self.addr.delete()
        if self.chan:
            self.chan.delete()

class SourceRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('tree header'), related_name='source_tree_header', null=True)
    xref = models.IntegerField(_('identifier in the source system'), null=True)
    data_even = models.CharField(_('events recorded'), max_length=90, blank=True, null=True)
    data_date = models.CharField(_('date period'), max_length=35, blank=True, null=True)
    data_plac = models.CharField(_('source jurisdiction place'), max_length=120, blank=True, null=True)
    data_agnc = models.CharField(_('responsible agency'), max_length=120, blank=True, null=True)
    auth = models.TextField(_('source originator'), blank=True, null=True)
    titl = models.TextField(_('source descriptive title'), blank=True, null=True)
    abbr = models.CharField(_('source field by entry'), max_length=60, blank=True, null=True)
    publ = models.TextField(_('source publication facts'), blank=True, null=True)
    text = models.TextField(_('text from source'), blank=True, null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('change_date'), related_name='source_change_date', null=True)
    _upd = models.CharField(_('custom field: update'), max_length=40, blank=True, null=True)
    _type = models.CharField(_('custom field: type'), max_length=40, blank=True, null=True)
    _medi = models.CharField(_('custom field: media id'), max_length=40, blank=True, null=True)
    _uid = models.CharField(_('custom field: uid'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

    def before_delete(self):
        if self.chan:
            self.chan.delete()

class SourceRepositoryCitation(models.Model):
    repo = models.ForeignKey(RepositoryRecord, on_delete=models.CASCADE, verbose_name=_('citation repository'), related_name='citation_repository', null=True)
    sour = models.ForeignKey(SourceRecord, on_delete=models.CASCADE, verbose_name=_('citation source'), related_name='citation_source', null=True)
    caln = models.CharField(_('source call number'), max_length=120, blank=True, null=True)
    caln_medi = models.CharField(_('source media type'), max_length=15, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

class SubmitterRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('tree header'), related_name='submitter_tree_header', null=True)
    xref = models.IntegerField(_('identifier in the source system'), null=True)
    name = models.CharField(_('submitter name'), max_length=60, blank=True, null=True)
    addr = models.ForeignKey(AddressStructure, on_delete=models.SET_NULL, verbose_name=_('address'), related_name='submitter_address', null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('change_date'), related_name='submitter_change_date', null=True)
    _uid = models.CharField(_('custom field: uid'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

    def before_delete(self):
        if self.addr:
            self.addr.delete()
        if self.chan:
            self.chan.delete()

#--------------------------------------------------
class AlbumRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('tree header'), related_name='album_tree_header', null=True)
    xref = models.IntegerField(_('identifier in the source system'), null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('change_date'), related_name='album_change_date', null=True)
    titl = models.CharField(_('title'), max_length=250, blank=True, null=True)
    desc = models.CharField(_('title'), max_length=250, blank=True, null=True)
    _upd = models.CharField(_('custom field: update'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

    def before_delete(self):
        if self.chan:
            self.chan.delete()

#--------------------------------------------------
class MultimediaRecord(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('tree header'), related_name='mm_tree_header', null=True)
    xref = models.IntegerField(_('identifier in the source system'), null=True)
    rin = models.CharField(_('RIN'), max_length=12, blank=True, null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.SET_NULL, verbose_name=_('change_date'), related_name='mfile_change_date', null=True)
    _size = models.CharField(_('custom field: file size'), max_length=15, blank=True, null=True)
    _date = models.CharField(_('custom field: date'), max_length=15, blank=True, null=True)
    _plac = models.CharField(_('custom field: place'), max_length=250, blank=True, null=True)
    _prim = models.CharField(_('custom field: prim'), max_length=1, blank=True, null=True)
    _cuto = models.CharField(_('custom field: cutout'), max_length=1, blank=True, null=True)
    _pari = models.CharField(_('custom field: parent rin'), max_length=100, blank=True, null=True)
    _pers = models.CharField(_('custom field: personal photo'), max_length=1, blank=True, null=True)
    _prcu = models.CharField(_('custom field: prim cutout'), max_length=1, blank=True, null=True)
    _pare = models.CharField(_('custom field: parent photo'), max_length=1, blank=True, null=True)
    _prin = models.CharField(_('custom field: parent RIN'), max_length=12, blank=True, null=True)
    _posi = models.CharField(_('custom field: position'), max_length=50, blank=True, null=True)
    _albu = models.ForeignKey(AlbumRecord, on_delete=models.SET_NULL, verbose_name=_('album'), related_name='mfile_album', null=True)
    _uid = models.CharField(_('custom field: uid'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

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
    obje = models.ForeignKey(MultimediaRecord, on_delete=models.CASCADE, verbose_name=_('multimedia record'), related_name='multimedia_record_file', null=True)
    file = models.CharField(_('multimedia file reference'), max_length=259, blank=True, null=True)
    form = models.CharField(_('multimedia format'), max_length=4, blank=True, null=True)
    type = models.CharField(_('source media type'), max_length=15, blank=True, null=True)
    medi = models.CharField(_('source media type'), max_length=15, blank=True, null=True)
    titl = models.CharField(_('descriptive title'), max_length=248, blank=True, null=True)
    _fdte = models.CharField(_('custom field: fdte'), max_length=50, blank=True, null=True)
    _fplc = models.CharField(_('custom field: fplc'), max_length=250, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

#--------------------------------------------------
class SourceCitation(models.Model):
    fam = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('family'), related_name='source_citation_family', null=True)
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('individual'), related_name='source_citation_individual', null=True)
    asso = models.ForeignKey(AssociationStructure, on_delete=models.CASCADE, verbose_name=_('association'), related_name='source_citation_association', null=True)
    obje = models.ForeignKey(MultimediaRecord, on_delete=models.CASCADE, verbose_name=_('multimedia'), related_name='source_citation_multimedia', null=True)
    even = models.ForeignKey(EventDetail, on_delete=models.CASCADE, verbose_name=_('event_detail'), related_name='source_citation_event_detail', null=True)
    pnpi = models.ForeignKey(PersonalNamePieces, on_delete=models.CASCADE, verbose_name=_('personal_name_pieces'), related_name='source_citation_personal_name_pieces', null=True)
    note = models.ForeignKey(NoteRecord, on_delete=models.CASCADE, verbose_name=_('note'), related_name='source_citation_note', null=True)
    sour = models.ForeignKey(SourceRecord, on_delete=models.CASCADE, verbose_name=_('source'), related_name='source_citation_source', null=True)
    page = models.CharField(_('where within source'), max_length=248, blank=True, null=True)
    even_even = models.CharField(_('event type cited from'), max_length=15, blank=True, null=True)
    even_role = models.CharField(_('role in event'), max_length=27, blank=True, null=True)
    data_date = models.CharField(_('entry recording date'), max_length=90, blank=True, null=True)
    data_text = models.TextField(_('text from source'), blank=True, null=True)
    quay = models.CharField(_('certainty assessment'), max_length=1, blank=True, null=True)
    auth = models.CharField(_('author'), max_length=120, blank=True, null=True)
    titl = models.CharField(_('title'), max_length=250, blank=True, null=True)
    _upd = models.CharField(_('custom field: update'), max_length=40, blank=True, null=True)
    _type = models.CharField(_('custom field: type'), max_length=40, blank=True, null=True)
    _medi = models.CharField(_('custom field: media id'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

class FamilySourceCitation(models.Model):
    fami = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('family'), related_name='family_source_citation_family')
    soci = models.ForeignKey(SourceCitation, on_delete=models.CASCADE, verbose_name=_('source_citation'), related_name='family_source_citation')

#--------------------------------------------------
class MultimediaLink(models.Model):
    obje = models.ForeignKey(MultimediaRecord, on_delete=models.CASCADE, verbose_name=_('multimedia'), related_name='multimedia_link', null=True)
    fam = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('family'), related_name='family_mm_link', null=True)
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('individual'), related_name='individual_mm_link', null=True)
    cita = models.ForeignKey(SourceCitation, on_delete=models.CASCADE, verbose_name=_('source citation'), related_name='source_citation_mm_link', null=True)
    sour = models.ForeignKey(SourceRecord, on_delete=models.CASCADE, verbose_name=_('source'), related_name='source_mm_link', null=True)
    subm = models.ForeignKey(SubmitterRecord, on_delete=models.CASCADE, verbose_name=_('submitter'), related_name='submitter_mm_link', null=True)
    even = models.ForeignKey(EventDetail, on_delete=models.CASCADE, verbose_name=_('event_detail'), related_name='event_detail_mm_link', null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

#--------------------------------------------------
class NoteStructure(models.Model):
    tree = models.ForeignKey(FamTree, on_delete=models.CASCADE, verbose_name=_('gedcom content description'), related_name='note_structure_tree_note', null=True)
    fam = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('family'), related_name='family_note', null=True)
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('individual'), related_name='individual_note', null=True)
    cita = models.ForeignKey(SourceCitation, on_delete=models.CASCADE, verbose_name=_('source citation'), related_name='source_citation_note', null=True)
    asso = models.ForeignKey(AssociationStructure, on_delete=models.CASCADE, verbose_name=_('association'), related_name='association_note', null=True)
    chan = models.ForeignKey(ChangeDate, on_delete=models.CASCADE, verbose_name=_('change_date'), related_name='change_date_note', null=True)
    famc = models.ForeignKey(ChildToFamilyLink, on_delete=models.CASCADE, verbose_name=_('child to family link'), related_name='ctfl_date_note', null=True)
    obje = models.ForeignKey(MultimediaRecord, on_delete=models.CASCADE, verbose_name=_('multimedia'), related_name='multimedia_note', null=True)
    repo = models.ForeignKey(RepositoryRecord, on_delete=models.CASCADE, verbose_name=_('repository'), related_name='repository_note', null=True)
    sour = models.ForeignKey(SourceRecord, on_delete=models.CASCADE, verbose_name=_('source'), related_name='source_note', null=True)
    srci = models.ForeignKey(SourceRepositoryCitation, on_delete=models.CASCADE, verbose_name=_('source repository citation'), related_name='source_repository_citation_note', null=True)
    subm = models.ForeignKey(SubmitterRecord, on_delete=models.CASCADE, verbose_name=_('submitter'), related_name='submitter_note', null=True)
    even = models.ForeignKey(EventDetail, on_delete=models.CASCADE, verbose_name=_('event_detail'), related_name='event_detail_note', null=True)
    pnpi = models.ForeignKey(PersonalNamePieces, on_delete=models.CASCADE, verbose_name=_('personal_name_pieces'), related_name='personal_name_pieces_note', null=True)
    plac = models.ForeignKey(PlaceStructure, on_delete=models.CASCADE, verbose_name=_('place'), related_name='place_note', null=True)
    note = models.ForeignKey(NoteRecord, on_delete=models.CASCADE, verbose_name=_('note'), related_name='note_structure_note', null=True)
    mode = models.IntegerField(_('which part of noted structure'), default=0)
    _sort = models.IntegerField(_('sort order'), null=True)

class UserReferenceNumber(models.Model):
    indi = models.ForeignKey(IndividualRecord, on_delete=models.CASCADE, verbose_name=_('individual'), related_name='individual_refn', null=True)
    fam  = models.ForeignKey(FamRecord, on_delete=models.CASCADE, verbose_name=_('family'), related_name='family_refn', null=True)
    obje = models.ForeignKey(MultimediaRecord, on_delete=models.CASCADE, verbose_name=_('multimedia record'), related_name='multimedia_record_refn', null=True)
    note = models.ForeignKey(NoteRecord, on_delete=models.CASCADE, verbose_name=_('note'), related_name='note_refn')
    repo = models.ForeignKey(RepositoryRecord, on_delete=models.CASCADE, verbose_name=_('repository'), related_name='repository_refn', null=True)
    sour = models.ForeignKey(SourceRecord, on_delete=models.CASCADE, verbose_name=_('source'), related_name='source_refn', null=True)
    refn = models.CharField(_('user reference number'), max_length=20, blank=True, null=True)
    type = models.CharField(_('user reference type'), max_length=40, blank=True, null=True)
    _sort = models.IntegerField(_('sort order'), null=True)

class Params(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name = 'genealogy_user')
    cur_tree = models.ForeignKey(FamTree, on_delete=models.SET_NULL, verbose_name=_('current tree'), related_name='users_current_tree', null=True)

    @classmethod
    def get_cur_tree(cls, user):
        if Params.objects.filter(user=user.id).exists():
            params = Params.objects.filter(user=user.id).get()
            if FamTree.objects.filter(id=params.cur_tree.id).exists():
                return params.cur_tree
        if len(FamTree.objects.all()) > 0:
            tree = FamTree.objects.all().order_by('sort')[0]
            Params.set_cur_tree(user, tree)
            return tree
        return None

    @classmethod
    def set_cur_tree(cls, user, tree):
        if user and tree:
            if not Params.objects.filter(user=user.id).exists():
                Params.objects.create(user=user, cur_tree=tree)
            else:
                params = Params.objects.filter(user=user.id).get()
                params.cur_tree = tree
                params.save()

    @classmethod
    def get_cur_indi(cls, user, tree=None):
        if not tree:
            tree = cls.get_cur_tree(user)
        if not tree:
            return None
        if tree.cur_indi:
            if IndividualRecord.objects.filter(id=tree.cur_indi).exists():
                indi = IndividualRecord.objects.filter(id=tree.cur_indi).get()
                return indi
            cls.set_cur_indi(tree, None)
        if IndividualRecord.objects.filter(tree=tree.id).exists():
            indi = IndividualRecord.objects.filter(tree=tree.id)[0]
            Params.set_cur_indi(tree, indi)
            return indi
        return None
            
    @classmethod
    def set_cur_indi(cls, tree, indi):
        if tree:
            if not indi:
                tree.cur_indi = None
            else:
                tree.cur_indi = indi.id
        tree.save()

#####################################################################################################
# Views
#             

class IndiInfo(models.Model):
    id = models.IntegerField('id', primary_key=True, null=False)
    tree_id = models.IntegerField(_('tree id'), null=False)
    sex = models.CharField(_('sex'), max_length=1, blank=True, null=True)
    pns_id = models.IntegerField(_('person name structure id'), null=True)
    pnp_id = models.IntegerField(_('person name pieces id'), null=True)
    givn = models.CharField(_('given name'), max_length=120, blank=True, null=True)
    surn = models.CharField(_('surname'), max_length=120, blank=True, null=True)
    _marnm = models.CharField(_('custom field: married name'), max_length=120, blank=True, null=True)
    birth_date = models.CharField(_('date of birth'), max_length=15, blank=True, null=True)
    birth_place = models.CharField(_('place of birth'), max_length=120, blank=True, null=True)
    death_date = models.CharField(_('date of death'), max_length=15, blank=True, null=True)
    death_place = models.CharField(_('place of death'), max_length=120, blank=True, null=True)
    age = models.IntegerField(_('age'), null=True)
    mmr_id = models.IntegerField(_('multimedia record id'), null=True)
    mmr_prim = models.CharField(_('primary'), max_length=1, blank=True, null=True)
    file = models.CharField(_('file name'), max_length=259, blank=True, null=True)
    mmr_posi = models.CharField(_('positions'), max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'family_vw_indi'

    def thumbnail(self):
        if self.mmr_id:
            return reverse('family:thumbnail', args=(self.tree_id,)) + '?mmr=' + str(self.mmr_id)
        if self.sex == 'M':
            return '/static/img/man.jpg'
        return '/static/img/woman.jpg'

    def name(self):
        return self.givn + ' ' + self.surn

PEDI_SELECT   = [('birth', _('birth')), ('adopted', _('adopted')), ('foster', _('foster'))]

class IndiFamilies(models.Model):
    id = models.IntegerField(_('id'), primary_key=True, null=False)
    tree_id = models.IntegerField(_('tree id'), null=False)
    chil_id = models.IntegerField(_('child id'), null=False)
    fami_id = models.IntegerField(_('family id'), null=False)
    husb_id = models.IntegerField(_('husband id'), null=False)
    husb_givn = models.CharField(_('husband given name'), max_length=120, blank=True, null=True)
    husb_surn = models.CharField(_('husband surname'), max_length=120, blank=True, null=True)
    husb_role = models.CharField(_('husband role'), choices=PARENT_RELAT_SELECT, max_length=20, blank=True, null=True)
    husb_mmr_id = models.IntegerField(_('husband multimedia record id'), null=True)
    wife_id = models.IntegerField(_('wife id'), null=False)
    wife_givn = models.CharField(_('wife given name'), max_length=120, blank=True, null=True)
    wife_surn = models.CharField(_('wife surname'), max_length=120, blank=True, null=True)
    wife_role = models.CharField(_('wife role'), choices=PARENT_RELAT_SELECT, max_length=20, blank=True, null=True)
    wife_mmr_id = models.IntegerField(_('wife multimedia record id'), null=True)
    pedi = models.CharField(_('pedigree linkage type').capitalize(), max_length=20, blank=True, null=True, choices=PEDI_SELECT, default='birth')

    class Meta:
        managed = False
        db_table = 'family_vw_indi_families'

    def husb_thumbnail(self):
        if self.husb_mmr_id:
            return reverse('family:thumbnail_100', args=(self.tree_id,)) + '?mmr=' + str(self.husb_mmr_id)
        return '/static/img/man.jpg'

    def wife_thumbnail(self):
        if self.wife_mmr_id:
            return reverse('family:thumbnail_100', args=(self.tree_id,)) + '?mmr=' + str(self.wife_mmr_id)
        return '/static/img/woman.jpg'

class IndiSpouses(models.Model):
    id = models.IntegerField(_('id'), primary_key=True, null=False)
    spou_sort = models.CharField(_('spouses sorting field'), max_length=50, blank=True, null=True)
    tree_id = models.IntegerField(_('tree id'), null=False)
    fami_id = models.IntegerField(_('family id'), null=False)
    indi_id = models.IntegerField(_('person id'), null=False)
    spou_id = models.IntegerField(_('spouse id'), null=False)
    spou_mmr_id = models.IntegerField(_('spouse multimedia record id'), null=True)
    givn = models.CharField(_('spouse given name'), max_length=120, blank=True, null=True)
    surn = models.CharField(_('spouse surname'), max_length=120, blank=True, null=True)
    _marnm = models.CharField(_('spouse marriage name'), max_length=120, blank=True, null=True)
    tag = models.CharField(_('family event tag'), max_length=10, blank=True, null=True)
    value = models.CharField(_('family event value'), max_length=150, blank=True, null=True)
    desc = models.CharField(_('family event description'), max_length=250, blank=True, null=True)
    husb_age = models.CharField(_('husband age'), max_length=20, blank=True, null=True)
    wife_age = models.CharField(_('wife age'), max_length=20, blank=True, null=True)
    type = models.CharField(_('event or fact classification'), max_length=90, blank=True, null=True)
    date = models.CharField(_('family event date'), max_length=50, blank=True, null=True)
    sort = models.CharField(_('family event date in sortable format'), max_length=50, blank=True, null=True)
    agnc = models.CharField(_('responsible agency'), max_length=120, blank=True, null=True)
    reli = models.CharField(_('religious affiliation'), max_length=90, blank=True, null=True)
    caus = models.CharField(_('cause of event'), max_length=90, blank=True, null=True)
    plac = models.CharField(_('place name'), max_length=120, blank=True, null=True)
    map_lati = models.CharField(_('latitude'), max_length=10, blank=True, null=True)
    map_long = models.CharField(_('longitude'), max_length=11, blank=True, null=True)
    addr = models.CharField(_('address value'), max_length=500, blank=True, null=True)
    addr_adr1 = models.CharField(_('address line 1'), max_length=60, blank=True, null=True)
    addr_adr2 = models.CharField(_('address line 2'), max_length=60, blank=True, null=True)
    addr_adr3 = models.CharField(_('address line 3'), max_length=60, blank=True, null=True)
    addr_city = models.CharField(_('city'), max_length=60, blank=True, null=True)
    addr_stae = models.CharField(_('state'), max_length=60, blank=True, null=True)
    addr_post = models.CharField(_('postal code'), max_length=10, blank=True, null=True)
    addr_ctry = models.CharField(_('country'), max_length=60, blank=True, null=True)
    phon = models.CharField(_('phone number'), max_length=25, blank=True, null=True)
    phon2 = models.CharField(_('phone number 2'), max_length=25, blank=True, null=True)
    phon3 = models.CharField(_('phone number 3'), max_length=25, blank=True, null=True)
    email = models.CharField(_('email'), max_length=120, blank=True, null=True)
    email2 = models.CharField(_('email 2'), max_length=120, blank=True, null=True)
    email3 = models.CharField(_('email 3'), max_length=120, blank=True, null=True)
    fax = models.CharField(_('fax'), max_length=60, blank=True, null=True)
    fax2 = models.CharField(_('fax 2'), max_length=60, blank=True, null=True)
    fax3 = models.CharField(_('fax 3'), max_length=60, blank=True, null=True)
    www = models.CharField(_('web page'), max_length=2047, blank=True, null=True)
    www2 = models.CharField(_('web page 2'), max_length=2047, blank=True, null=True)
    www3 = models.CharField(_('web page 3'), max_length=2047, blank=True, null=True)
    owner = models.CharField(_('owner of this record'), max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'family_vw_indi_spouses'

    def spou_thumbnail(self):
        if self.spou_mmr_id:
            return reverse('family:thumbnail_100', args=(self.tree_id,)) + '?mmr=' + str(self.spou_mmr_id)
        return '/static/img/man.jpg'

