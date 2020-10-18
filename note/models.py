from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from todo.models import Lst
from hier.files import get_files_list
from hier.models import get_app_params
from hier.categories import get_categories_list

app_name = 'note'

#----------------------------------
class Note(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name  = models.CharField(_('name'), max_length = 200, blank = False)
    code  = models.CharField(_('code'), max_length = 200, blank = True)
    descr = models.TextField(_('description'), blank = True)
    publ  = models.DateTimeField(_('publication date'), blank=True, default = datetime.now)
    lst = models.ForeignKey(Lst, on_delete = models.CASCADE, verbose_name = _('list'), blank = True, null = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)
    url = models.CharField(_('URL'), max_length=2000, blank = True)
    categories = models.CharField(_('categories'), max_length = 2000, blank = True, default = '', null = True)
    kind  = models.CharField(_('kind of note'), max_length = 200, blank = True, default = 'note')

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')

    def __str__(self):
        return self.name

    def get_info(self):
        ret = []

        if (self.kind == 'news'):
            ret.append({'text': self.publ.strftime('%d.%m.%Y %H:%M')})

        if self.lst:
            app_param = get_app_params(self.user, self.kind)
            if (app_param.restriction != 'list'):
                if ret:
                    ret.append({'icon': 'separator'})
                ret.append({'text': self.lst.name})

        if self.code:
            if ret:
                ret.append({'icon': 'separator'})
            ret.append({'text': '{}: {}'.format(_('code'), self.code) })

        files = get_files_list(self.user, app_name, 'note_{}'.format(self.id))
    
        if ret and (self.url or self.descr or len(files)):
            ret.append({'icon': 'separator'})
    
        if self.url:
            ret.append({'icon': 'url'})
    
        if self.descr:
            ret.append({'icon': 'notes'})
    
        if len(files):
            ret.append({'icon': 'attach'})

        if self.categories:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            categs = get_categories_list(self.categories)
            for categ in categs:
                ret.append({'icon': 'category', 'text': categ.name, 'color': 'category-design-' + categ.design})
    
        return ret
