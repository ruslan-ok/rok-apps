import random
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from todo.models import Lst
from hier.models import Lst

app_name = 'store'

ALPHA_GROUPS = {
    'uc': 'ABCDEFGHJKLMNPQRSTUVWXYZ',
    'uc_': 'IO',
    'lc': 'abcdefghjkmnpqrstuvwxyz',
    'lc_': 'io',
    'dg': '23456789',
    'dg_': '10',
    'sp': '!@#$%^&*=+',
    'br': '()[]{}<>',
    'mi': '-',
    'ul': '_',
}

#----------------------------------
# deprecated
class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    code = models.CharField(_('code'), max_length=100, blank = True)
    name = models.CharField(_('name'), max_length=300)
    uuid = models.CharField(_('UUID'), max_length=100, blank = True)
    creation = models.DateTimeField(_('creation time'), null = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), null = True, auto_now = True)

#----------------------------------
class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    title = models.CharField(_('title'), max_length=500)
    username = models.CharField(_('username'), max_length=150, blank=True)
    value = models.CharField(_('value'), max_length=128)
    url = models.CharField(_('URL'), max_length=2000, blank = True)
    notes = models.TextField(_('notes'), blank = True, null = True)
    uuid = models.CharField(_('UUID'), max_length=100, blank = True)
    created = models.DateTimeField(_('creation time'), auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True, null = True)
    # group - deprecated
    group = models.ForeignKey(Group, verbose_name = _('group'), on_delete = models.CASCADE, null = True)
    actual = models.IntegerField(_('actual'), default = 1)
    categories = models.CharField(_('categories'), max_length = 2000, blank = True, default = '', null = True)
    params = models.IntegerField(_('generator parameters used'), default = 0, null = True)
    lst = models.ForeignKey(Lst, on_delete = models.CASCADE, verbose_name = _('list'), blank = True, null = True)

    @classmethod
    def get_new_value(cls, user):
        if (len(Params.objects.filter(user = user.id)) > 0):
            params = Params.objects.filter(user = user.id)[0]
        else:
            params = Params.objects.create(user = user)

        allowed_groups = []
        if params.uc:
            allowed_groups.append('uc')
            if not params.ac:
                allowed_groups.append('uc_')
        if params.lc:
            allowed_groups.append('lc')
            if not params.ac:
                allowed_groups.append('lc_')
        if params.dg:
            allowed_groups.append('dg')
            if not params.ac:
                allowed_groups.append('dg_')
        if params.sp:
            allowed_groups.append('sp')
        if params.br:
            allowed_groups.append('br')
        if params.mi:
            allowed_groups.append('mi')
        if params.ul:
            allowed_groups.append('ul')

        allowed_chars = ''
        for x in allowed_groups:
            allowed_chars += ALPHA_GROUPS[x]

        if (allowed_chars == ''):
            allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*(-_=+)'

        ret_params = 0
        if params.uc:
            ret_params += 1
        if params.lc:
            ret_params += 2
        if params.dg:
            ret_params += 4
        if params.sp:
            ret_params += 8
        if params.br:
            ret_params += 16
        if params.mi:
            ret_params += 32
        if params.ul:
            ret_params += 64
        if params.ac:
            ret_params += 128

        ret_value = ''
        len_rest = params.ln
        for i in range(len(allowed_groups)):
            grp = random.choice(allowed_groups)
            allowed_groups.remove(grp)
            wrk = ALPHA_GROUPS[grp]
            ret_value += get_random_string(1, wrk)
            len_rest -= 1
        ret_value += get_random_string(len_rest, allowed_chars)
        return ret_params, params.un, ret_value

#----------------------------------
# deprecated
class History(models.Model):
    node = models.ForeignKey(Entry, verbose_name = _('node'), on_delete = models.CASCADE, related_name='node')
    data = models.ForeignKey(Entry, verbose_name = _('entry'), on_delete = models.CASCADE, related_name='data')

#----------------------------------
class Params(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='store_user')
    ln = models.IntegerField(_('length').capitalize(), default = 20)
    uc = models.BooleanField(_('upper case').capitalize(), default = True)
    lc = models.BooleanField(_('lower case').capitalize(), default = True)
    dg = models.BooleanField(_('digits').capitalize(), default = True)
    sp = models.BooleanField(_('special symbols').capitalize(), default = True)
    br = models.BooleanField(_('brackets').capitalize(), default = True)
    mi = models.BooleanField(_('minus').capitalize(), default = True)
    ul = models.BooleanField(_('underline').capitalize(), default = True)
    ac = models.BooleanField(_('avoid confusion').capitalize(), default = True)
    un = models.CharField(_('default username'), max_length=160, blank=True, default='')


