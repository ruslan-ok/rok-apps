import json
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.urls import NoReverseMatch
from django.utils.translation import gettext_lazy as _
from task.const import *
from rest_framework.reverse import reverse


class CurrencyRate(models.Model):
    currency = models.CharField('Currency', max_length=10, blank=False)
    base = models.CharField('Base currency', max_length=10, blank=True, default='USD')
    rate_date = models.DateField('Rate Date', blank=False, null=False)
    num_units = models.IntegerField('Number of units exchanged', null=False, default=1)
    value = models.DecimalField('Exchange rate to USD', blank=True, null=True, max_digits=15, decimal_places=4)
    source = models.CharField('Data source', max_length=200, blank=True)
    info = models.CharField('Comment', max_length=1000, blank=True)

    def __repr__(self):
        return f'CurrencyRate {self.id} "{self.currency}" -> {self.base} [{self.rate_date.strftime("%Y.%m.%d")}] = {self.value} ({self.source})'


class CurrencyApis(models.Model):
    name = models.CharField('Name', max_length=100, blank=False)
    prioritet = models.IntegerField('Prioritet', default=1, null=False)
    api_url = models.CharField('URL for rate on date', max_length=1000, blank=False)
    token = models.CharField('Phrase for exhausted limit', max_length=1000, blank=True)
    value_path = models.CharField('json path to value', max_length=1000, blank=True)
    phrase = models.CharField('Phrase for exhausted limit', max_length=1000, blank=True)
    next_try = models.DateField('Next try Date', null=True)
    today_avail = models.BooleanField('Today rate is available', null=True, default=True)
    weekdays_avail = models.BooleanField('Weekdays rate is available', null=True, default=True)
    base = models.CharField('Base currency', max_length=10, blank=True)


class Group(models.Model):
    """
    Item groups
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'), related_name='item_group_user')
    app = models.CharField(_('App name'), max_length=50, blank=False, null=True)
    role = models.CharField(_('Role name'), max_length=50, blank=False, null=True)
    node = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name=_('Node'), blank=True, null=True)
    name = models.CharField(_('Group name'), max_length=200, blank=False)
    sort = models.CharField(_('Sort code'), max_length=50, blank=True)
    created = models.DateTimeField(_('Creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('Last modification time'), blank=True, auto_now=True)
    completed = models.BooleanField(_('Display completed records'), null=True)
    theme = models.IntegerField(_('Theme id'), blank=True, null=True)
    sub_groups = models.CharField(_('Content items sub groups'), max_length=10000, blank=True, null=True)
    use_sub_groups = models.BooleanField(_('Using content items sub groups'), null=True)
    parameters = models.IntegerField(_('Additional group parameters'), null=True)
    determinator = models.CharField(_('Group category: "group", "role" or "view"'), max_length=10, blank=True, null=True)
    view_id = models.CharField(_('View identificator for "role" and "view"'), max_length=50, blank=True, null=True)
    items_sort = models.CharField(_('Items sorting orders'), max_length=500, blank=True)
    info = models.TextField(_('Information'), blank=True, null=True)
    act_items_qty = models.IntegerField(_('Items in group'), blank=True, null=True)

    class Meta:
        verbose_name=_('Item group')
        verbose_name_plural = _('Item groups')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return '.' * self.level() + self.name

    def s_id(self):
        return str(self.id)
    
    def get_shifted_name(self):
        return '.'*self.level()*2 + self.name
    
    def edit_url(self):
        if not self.app or (self.app == APP_ALL) or (self.app == APP_HOME):
            return 'todo:group'
        return self.app + ':group'

    def level(self):
        ret = 0
        node = self.node
        while node:
            ret += 1
            node = node.node
        return ret

    def is_leaf(self):
        return not Group.objects.filter(node=self.id).exists()

    def toggle_sub_group(self, sub_group_id):
        if self.sub_groups:
            sgs = json.loads(self.sub_groups)
            for sg in sgs:
                if (sg['id'] == int(sub_group_id)):
                    sg['is_open'] = not sg['is_open']
            self.sub_groups = json.dumps(sgs)
            self.save()

    def set_theme(self, theme_id):
        self.theme = theme_id
        self.save()

    def dark_theme(self):
        if not self.theme:
            return False
        return (self.theme < 8) or (self.theme > 14)

    def set_sort(self, sort_id):
        if self.items_sort.replace('-', '') == sort_id:
            if self.items_sort.replace('-', '') == self.items_sort:
                self.items_sort = '-' + sort_id
            else:
                self.items_sort = sort_id
        else:
            self.items_sort = sort_id
        self.save()

    def reverse_sort(self):
        if not self.items_sort:
            return
        if self.items_sort.replace('-', '') == self.items_sort:
            self.items_sort = '-' + self.items_sort
        else:
            self.items_sort = self.items_sort[1:]
        self.save()

    def delete_sort(self):
        self.items_sort = ''
        self.save()

    def get_absolute_url(self):
        if not self.app or not self.role:
            return '/'
        try:
            url = reverse(self.app + ':' + self.role + '-item', args = [self.id])
            return url
        except NoReverseMatch:
            return '/'


class Item(models.Model):
    """
    An Entity that can be a Task or something else
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'), related_name='item_user')
    app = models.CharField(_('App name'), max_length=50, blank=False, null=True)
    role = models.CharField(_('Role name'), max_length=50, blank=False, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_('Group'), related_name='item_group', null=True)
    name = models.CharField(_('Name'), max_length=200, blank=True, null=True)
    categories = models.TextField(_('Categories'), blank=True, null=True)
    event = models.DateTimeField(_('Event date'), blank=True, null=True)
    start = models.DateField(_('Start date'), blank=True, null=True)
    stop = models.DateTimeField(_('Termin'), blank=True, null=True)
    info = models.TextField(_('Information'), blank=True, null=True)
    created = models.DateTimeField(_('Creation time'), default=datetime.now)
    last_mod = models.DateTimeField(_('Last modification time'), blank=True, auto_now=True)
    sort = models.CharField(_('Sort code'), max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        abstract = True

    def __str__(self):
        if self.name:
            return self.name
        return '?'

    def get_absolute_url(self):
        return self.get_url_for_app(self.app, self.role)

    def get_url_for_app(self, app, role):
        if not app:
            return '/'
        id = self.id
        try:
            if role:
                url = reverse(app + ':' + role + '-item', args = [id])
            else:
                url = reverse(app + ':item', args = [id])
            return url
        except NoReverseMatch:
            return '/'
    