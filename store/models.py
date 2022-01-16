from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from todo.models import Lst
from task.models import Task
from hier.models import Folder, Lst
from v2_hier.categories import get_categories_list

app_name = 'store'

#----------------------------------
# deprecated
class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    code = models.CharField(_('code'), max_length=100, blank = True)
    name = models.CharField(_('name'), max_length=300)
    uuid = models.CharField(_('UUID'), max_length=100, blank = True)
    creation = models.DateTimeField(_('creation time'), null = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), null = True, auto_now = True)

    def __str__(self):
        return self.name

    def qty(self):
        return len(Entry.objects.filter(group = self.id))
 

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

        allowed_chars = ''
        
        if params.uc:
            allowed_chars = allowed_chars + 'ABCDEFGHJKLMNPQRSTUVWXYZ'
            if not params.ac:
                allowed_chars = allowed_chars + 'IO'
        
        if params.lc:
            allowed_chars = allowed_chars + 'abcdefghjkmnpqrstuvwxyz'
            if not params.ac:
                allowed_chars = allowed_chars + 'io'

        if params.dg:
            allowed_chars = allowed_chars + '23456789'
            if not params.ac:
                allowed_chars = allowed_chars + '10'

        if params.sp:
            allowed_chars = allowed_chars + '!@#$%^&*=+'

        if params.br:
            allowed_chars = allowed_chars + '()[]{}<>'
        
        if params.mi:
            allowed_chars = allowed_chars + '-'
        
        if params.ul:
            allowed_chars = allowed_chars + '_'

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

        ret_value = get_random_string(params.ln, allowed_chars)
        return ret_params, params.un, ret_value

    def __str__(self):
        return self.title

    def name(self):
        return self.title

    def marked_item(self):
        return (self.actual != 1)

    def have_notes(self):
        if (self.notes == None) or (self.notes == ''):
            return ''
        else:
            return '@'

    def get_info(item):
        ret = []
        
        if item.lst: # and (app_param.restriction != 'list'):
            ret.append({'text': item.lst.name})
    
        if item.username:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            ret.append({'text': item.username})
    
        if item.notes:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            ret.append({'icon': 'notes'})
    
        if item.categories:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            categs = get_categories_list(item.categories)
            for categ in categs:
                ret.append({'icon': 'category', 'text': categ.name, 'color': 'category-design-' + categ.design})
    
        return ret


#----------------------------------
# deprecated
class History(models.Model):
    node = models.ForeignKey(Entry, verbose_name = _('node'), on_delete = models.CASCADE, related_name='node')
    data = models.ForeignKey(Entry, verbose_name = _('entry'), on_delete = models.CASCADE, related_name='data')

    def __str__(self):
        return self.node.name


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

    class Meta:
        verbose_name = _('user settings')
        verbose_name_plural = _('user settings')


