from datetime import date, datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from genea.const import *

class GenDate(models.Model):
    mode = models.IntegerField(_('date value mode'), choices=DATE_VALUE_MODE, null=True) # default=DATE
    appr = models.IntegerField(_('date approximation mode'), choices=DATE_APPROXIMATION_MODE, null=True) # default=ABT
    range = models.IntegerField(_('date range mode'), choices=DATE_RANGE_MODE, null=True)
    beg = models.CharField(_('from date'), max_length=35, blank=True, null=True)
    end = models.CharField(_('to date'), max_length=35, blank=True, null=True)

class GenTree(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='genealogical_tree_user')
    mh_id = models.CharField(_('ID in MyHeritage.com'), max_length=50, blank=True, null=True)
    prj_id = models.CharField(_('project GUID'), max_length=200, blank=True, null=True)
    created = models.DateTimeField(_('creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)
    updated = models.CharField(_('update time'), max_length=50, blank=True, null=True)
    author = models.CharField(_('author'), max_length=200, blank=True, null=True)
    title = models.CharField(_('title'), max_length=1000, blank=True, null=True)
    info = models.TextField(_('information'), blank=True, null=True)
    type = models.CharField(_('type'), max_length=200, blank=True, null=True)
    media_id = models.IntegerField(_('media ID'), blank=True, null=True)
    gedcom_vers = models.CharField(_('GEDCOM version'), max_length=200, blank=True, null=True)
    gedcom_form = models.CharField(_('GEDCOM format'), max_length=200, blank=True, null=True)
    language = models.CharField(_('language'), max_length=200, blank=True, null=True)
    destination = models.CharField(_('destination'), max_length=200, blank=True, null=True)
    source = models.CharField(_('source'), max_length=200, blank=True, null=True)
    src_version = models.CharField(_('source version'), max_length=200, blank=True, null=True)
    src_name = models.CharField(_('source name'), max_length=200, blank=True, null=True)
    src_rtl = models.CharField(_('source RTL'), max_length=200, blank=True, null=True)
    src_corpo = models.CharField(_('source corpo'), max_length=200, blank=True, null=True)
    file = models.CharField(_('file RTL'), max_length=500, blank=True, null=True)

    def before_delete(self):
        for item in Person.objects.filter(tree=self.id):
            item.before_delete()
        for item in Family.objects.filter(tree=self.id):
            item.before_delete()

class GenAlbum(models.Model):
    tree = models.ForeignKey(GenTree, on_delete=models.CASCADE, verbose_name=_('tree'), related_name='genealogical_tree_album')
    mh_id = models.CharField(_('ID in MyHeritage.com'), max_length=50, blank=True, null=True)
    rin = models.CharField(_('RIN'), max_length=200, blank=True, null=True)
    print_sort = models.CharField(_('sort order'), max_length=100, blank=True, null=True)
    created = models.DateTimeField(_('creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)
    title = models.CharField(_('title'), max_length=200, blank=True, null=True)
    description = models.CharField(_('description'), max_length=200, blank=True, null=True)

class Person(models.Model):
    tree = models.ForeignKey(GenTree, on_delete=models.CASCADE, verbose_name=_('tree'), related_name='genealogical_tree_person')
    mh_id = models.CharField(_('ID in MyHeritage.com'), max_length=50, blank=True, null=True)
    print_sort = models.CharField(_('sort order'), max_length=100, blank=True, null=True)
    created = models.DateTimeField(_('creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)
    sex = models.CharField(_('sex'), max_length=200, blank=True, null=True)
    first_name = models.CharField(_('first (and middle) name'), max_length=200, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=200, blank=True, null=True)
    maiden_name = models.CharField(_('maiden name'), max_length=200, blank=True, null=True)
    prefix_name = models.CharField(_('prefix'), max_length=200, blank=True, null=True)
    suffix_name = models.CharField(_('suffix'), max_length=200, blank=True, null=True)
    relig_name = models.CharField(_('religious name'), max_length=200, blank=True, null=True)
    former_name = models.CharField(_('former name'), max_length=200, blank=True, null=True)
    nick_name = models.CharField(_('nickname'), max_length=200, blank=True, null=True)
    named_after = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name=_('named after (namesake)'), null=True)
    godparents = models.CharField(_('godparents'), max_length=200, blank=True, null=True)
    cause_of_death = models.CharField(_('cause of death'), max_length=200, blank=True, null=True)
    burial_place = models.CharField(_('burial place or cemetery'), max_length=200, blank=True, null=True)
    interests = models.CharField(_('interests'), max_length=200, blank=True, null=True)
    activities = models.CharField(_('activities'), max_length=200, blank=True, null=True)
    music = models.CharField(_('music'), max_length=200, blank=True, null=True)
    movies = models.CharField(_('movies'), max_length=200, blank=True, null=True)
    tv_shows = models.CharField(_('tv_shows'), max_length=200, blank=True, null=True)
    books = models.CharField(_('books'), max_length=200, blank=True, null=True)
    sports = models.CharField(_('sports'), max_length=200, blank=True, null=True)
    restaurants = models.CharField(_('restaurants'), max_length=200, blank=True, null=True)
    cuisines = models.CharField(_('cuisines'), max_length=200, blank=True, null=True)
    people = models.CharField(_('people and celebrities'), max_length=200, blank=True, null=True)
    getaways = models.CharField(_('getaways'), max_length=200, blank=True, null=True)
    quotes = models.CharField(_('quotes'), max_length=200, blank=True, null=True)
    religion = models.CharField(_('religion'), max_length=200, blank=True, null=True)
    nationalities = models.CharField(_('nationalities'), max_length=200, blank=True, null=True)
    lang_spoken = models.CharField(_('languages spoken'), max_length=200, blank=True, null=True)
    political_views = models.CharField(_('political views'), max_length=200, blank=True, null=True)
    height = models.CharField(_('height'), max_length=50, blank=True, null=True)
    weight = models.CharField(_('weight'), max_length=50, blank=True, null=True)
    hair_color = models.CharField(_('hair color'), max_length=50, blank=True, null=True)
    eye_color = models.CharField(_('eye color'), max_length=50, blank=True, null=True)
    phisical = models.TextField(_('phisical description'), blank=True, null=True)
    rin = models.CharField(_('RIN'), max_length=200, blank=True, null=True)
    uid = models.CharField(_('UID'), max_length=200, blank=True, null=True)

    def before_delete(self):
        for item in Media.objects.filter(person=self.id):
            item.before_delete()
        for item in PersContact.objects.filter(person=self.id):
            item.before_delete()
        for item in PersFact.objects.filter(person=self.id):
            item.before_delete()
        for item in PersSourceCitation.objects.filter(person=self.id):
            item.before_delete()
        for item in Media.objects.filter(person=self.id):
            item.before_delete()

class PersBio(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('person'), related_name='person_biography')
    info = models.TextField(_('information'), blank=True, null=True)

class PersContact(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('person'), related_name='person_contact')
    addr_1 = models.CharField(_('address'), max_length=200, blank=True, null=True)
    addr_2 = models.CharField(_('address (2)'), max_length=200, blank=True, null=True)
    city = models.CharField(_('city'), max_length=200, blank=True, null=True)
    country = models.CharField(_('country'), max_length=200, blank=True, null=True)
    state = models.CharField(_('state or province'), max_length=200, blank=True, null=True)
    zip = models.CharField(_('zip or postal code'), max_length=200, blank=True, null=True)
    details = models.ForeignKey(GenDate, on_delete=models.SET_NULL, verbose_name=_('details'), related_name='contact_details', null=True)
    email = models.CharField(_('email'), max_length=200, blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=200, blank=True, null=True)
    fax = models.CharField(_('fax'), max_length=200, blank=True, null=True)
    web_type = models.CharField(_('on the web'), max_length=200, blank=True, null=True)
    web_username = models.CharField(_('username'), max_length=200, blank=True, null=True)
    web_address = models.CharField(_('web address'), max_length=200, blank=True, null=True)
    note = models.TextField(_('information'), blank=True, null=True)

    def before_delete(self):
        if self.details:
            self.details.delete()

class PersFact(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('person'), related_name='person_fact')
    category = models.CharField(_('fact category'), max_length=50, blank=True, null=True)
    type = models.CharField(_('fact type'), max_length=50, blank=True, null=True)
    description = models.CharField(_('description'), max_length=500, blank=True, null=True)
    date = models.ForeignKey(GenDate, on_delete=models.SET_NULL, verbose_name=_('fact date'), related_name='pers_fact_date', null=True)
    age = models.CharField(_('person age'), max_length=50, blank=True, null=True)
    place = models.CharField(_('place'), max_length=500, blank=True, null=True)
    note = models.CharField(_('note'), max_length=500, blank=True, null=True)

    def before_delete(self):
        if self.date:
            self.date.delete()

class PersSourceCitation(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('person'), related_name='person_citat')
    tree = models.ForeignKey(GenTree, on_delete=models.CASCADE, verbose_name=_('tree'), related_name='source_tree')
    citation = models.TextField(_('citation text'), blank=True, null=True)
    page = models.CharField(_('page/URL'), max_length=200, blank=True, null=True)
    confidence = models.IntegerField(_('confidence'), choices=CONFIDENCE_MODE, default=NONE)
    date = models.ForeignKey(GenDate, on_delete=models.SET_NULL, verbose_name=_('date'), related_name='date_citat', null=True)
    event = models.CharField(_('event'), max_length=100, blank=True, null=True)

    def before_delete(self):
        if self.date:
            self.date.delete()

class Family(models.Model):
    tree = models.ForeignKey(GenTree, on_delete=models.CASCADE, verbose_name=_('tree'), related_name='genealogical_tree_family')
    husband = models.ForeignKey(Person, on_delete=models.SET_NULL, verbose_name=_('husband'), related_name='husband', null=True)
    wife = models.ForeignKey(Person, on_delete=models.SET_NULL, verbose_name=_('wife'), related_name='wife', null=True)
    relationship = models.IntegerField(_('relationship'), choices=RELATIONSHIP_MODE, null=True)
    print_sort = models.CharField(_('sort order'), max_length=100, blank=True, null=True)
    updated = models.CharField(_('update time'), max_length=50, blank=True, null=True)
    rin = models.CharField(_('RIN'), max_length=200, blank=True, null=True)
    uid = models.CharField(_('UID'), max_length=200, blank=True, null=True)

    def before_delete(self):
        for item in FamilyFact.objects.filter(family=self.id):
            item.before_delete()

class FamilyFact(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, verbose_name=_('family'), related_name='family_fact')
    category = models.CharField(_('fact category'), max_length=50, blank=True, null=True)
    type = models.CharField(_('fact type'), max_length=50, blank=True, null=True)
    description = models.CharField(_('description'), max_length=500, blank=True, null=True)
    date = models.ForeignKey(GenDate, on_delete=models.SET_NULL, verbose_name=_('fact date'), related_name='family_fact_date', null=True)
    place = models.CharField(_('place'), max_length=500, blank=True, null=True)
    note = models.CharField(_('note'), max_length=500, blank=True, null=True)

    def before_delete(self):
        if self.date:
            self.date.delete()

class FamilyChild(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, verbose_name=_('family'), related_name='family_children')
    child = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('child'), related_name='family_child')

class Media(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('person'), related_name='person_media')
    album = models.ForeignKey(GenAlbum, on_delete=models.CASCADE, verbose_name=_('album'), related_name='album_media', null=True)
    print_sort = models.CharField(_('sort order'), max_length=100, blank=True, null=True)
    created = models.DateTimeField(_('creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)
    format = models.CharField(_('media format'), max_length=20, blank=True, null=True)
    url = models.CharField(_('URL to media file'), max_length=500, blank=True, null=True)
    size = models.IntegerField(_('file size'), null=True)
    rin = models.CharField(_('RIN'), max_length=200, blank=True, null=True)
    title = models.CharField(_('title'), max_length=500, blank=True, null=True)
    date = models.ForeignKey(GenDate, on_delete=models.SET_NULL, verbose_name=_('media date'), related_name='media_date', null=True)
    place = models.CharField(_('place'), max_length=200, blank=True, null=True)
    prim = models.BooleanField(_('primary'), blank=True, null=True)
    cutout = models.BooleanField(_('cutout'), blank=True, null=True)
    parent_rin = models.CharField(_('parent RIN'), max_length=200, blank=True, null=True)
    prim_cutout = models.BooleanField(_('primary cutout'), blank=True, null=True)
    personal = models.BooleanField(_('personal photo'), blank=True, null=True)
    parent = models.BooleanField(_('parent photo'), blank=True, null=True)
    position = models.CharField(_('position'), max_length=100, blank=True, null=True)

    def before_delete(self):
        if self.date:
            self.date.delete()

