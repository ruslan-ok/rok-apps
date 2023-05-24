# from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from task.models import Group

class Lang(models.Model):
    code = models.fields.CharField('Language code', max_length=3, null=False, default='ru')
    name = models.fields.CharField('Language name', max_length=1000, null=False)

class Phrase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'cram_user')
    grp = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Group', blank=True, null=True)
    categories = models.TextField('Categories', blank=True, null=True)
    # note = models.TextField('Note', blank=True, null=True)
    # created = models.DateTimeField('Creation time', blank=True, default=datetime.now)
    # last_mod = models.DateTimeField('Last modification time', blank=True, auto_now=True)

class LangPhrase(models.Model):
    phrase = models.ForeignKey(Phrase, on_delete=models.SET_NULL, verbose_name='Phrase Id', related_name='phrase', null=True)
    lang = models.ForeignKey(Lang, on_delete=models.SET_NULL, verbose_name='Language code', related_name='phrase_language_code', null=True)
    text = models.TextField('Phrase', blank=True, null=True)
