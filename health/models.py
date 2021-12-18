from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Biomarker(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    publ = models.DateTimeField(_('when measurements were taken'), blank = True, default = datetime.now)
    height = models.IntegerField(_('height, cm'), blank = True, null = True)
    weight = models.DecimalField(_('weight, kg'), blank = True, null = True, max_digits = 5, decimal_places = 1)
    temp = models.DecimalField(_('temperature'), blank = True, null = True, max_digits = 4, decimal_places = 1)
    waist = models.IntegerField(_('waist circumference'), blank = True, null = True)
    systolic = models.IntegerField(_('systolic blood pressure'), blank = True, null = True)
    diastolic = models.IntegerField(_('diastolic blood pressure'), blank = True, null = True)
    pulse = models.IntegerField(_('the number of heartbeats per minute'), blank = True, null = True)
    info = models.TextField(_('information'), blank = True, default = "")

class Incident(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    name = models.CharField(_('name'), max_length = 100, blank = False)
    beg = models.DateField(_('start date of the incident'), blank = True, default = datetime.now)
    end = models.DateField(_('end date of the incident'), blank = True, default = datetime.now)
    diagnosis = models.CharField(_('diagnosis'), max_length = 1000, blank = True)
    info = models.TextField(_('information'), blank = True, default = "")

class Anamnesis(models.Model):
    incident = models.ForeignKey(Incident, on_delete = models.CASCADE, verbose_name = _('incident'))
    publ = models.DateTimeField(_('date of receipt'), blank = True, default = datetime.now)
    info = models.TextField(_('information'), blank = True, default = "")
