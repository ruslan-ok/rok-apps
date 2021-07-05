from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class PirTable(models.Model):
    name   = models.CharField(_('table'), max_length = 200, blank = False)

    class Meta:
        verbose_name = _('table')
        verbose_name_plural = _('tables')

    def __str__(self):
        return self.name


class PirPart(models.Model):
    table = models.ForeignKey(PirTable, on_delete=models.CASCADE, verbose_name=_('table'))
    name  = models.CharField(_('data block'), max_length = 200, blank = False)

    class Meta:
        verbose_name = _('part')
        verbose_name_plural = _('parts')

    def __str__(self):
        return self.table.name


class PirData(models.Model):
    table = models.ForeignKey(PirTable, on_delete=models.CASCADE, verbose_name=_('table'))
    part = models.ForeignKey(PirPart, on_delete=models.CASCADE, default = 1, verbose_name=_('part'))
    rec  = models.CharField(_('table record'), max_length = 1000, blank = False)

    class Meta:
        verbose_name = _('data')
        verbose_name_plural = _('datas')

    def __str__(self):
        return self.part.table.name + ' / ' + self.part.name + ' / ' + self.rec
