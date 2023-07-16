from datetime import datetime
from django.db import models
from django.db.models import Manager
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from task.models import Group
from task.const import APP_CRAM, ROLE_CRAM

class CramGroupManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(app=APP_CRAM, role=ROLE_CRAM)

class CramGroup(Group):
    objects = CramGroupManager()

    class Meta:
        proxy = True

    def __repr__(self):
        return f'CramGroup {self.id} "{self.name}"'

    def save(self, *args, **kwargs):
        self.app = APP_CRAM
        self.role = ROLE_CRAM
        super().save(*args, **kwargs)

    def check_items_qty(self):
        if (self.determinator == None) or (self.determinator == 'group'):
            self.act_items_qty = len(Phrase.objects.filter(group=self.id))
            self.save()
            qnt = 0

    def get_languages(self):
        lang_list = [x.code for x in Lang.objects.filter(user=self.user.id)]
        langs = []
        group_languages = self.currency.split(',')
        for lang_code in lang_list:
            if lang_code != 'ru' and self.currency and lang_code not in group_languages:
                continue
            langs.append(Lang.objects.get(user=self.user.id, code=lang_code))
        return langs

class Lang(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'lang_user')
    code = models.fields.CharField('Language code', max_length=3, null=False, default='ru')
    name = models.fields.CharField('Language name', max_length=1000, null=False)

    @classmethod
    def check_init(cls):
        if not Lang.objects.count():
            Lang.objects.create(code='ru', name='русский')
            Lang.objects.create(code='en', name='english')
            Lang.objects.create(code='pl', name='polski')

    def __str__(self):
        return f'Lang {self.code} "{self.name}"'

class GroupQuantityCorrectMode:
    ADD_PHRASE = 1 # Phrase created
    DEL_PHRASE = 2 # Phrase deleted

class Phrase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'cram_user')
    group = models.ForeignKey(CramGroup, on_delete=models.CASCADE, verbose_name='Group', blank=True, null=True)
    sort = models.fields.IntegerField('Sort code', null=False, default=1)
    categories = models.TextField('Categories', blank=True, null=True)

    def name(self):
        text = ''
        if Lang.objects.filter(user=self.user.id, code="ru").exists():
            ru = Lang.objects.filter(user=self.user.id, code="ru").get()
            if LangPhrase.objects.filter(phrase=self.id, lang=ru.id).exists():
                lp = LangPhrase.objects.filter(phrase=self.id, lang=ru.id).get()
                text = lp.text
        if not text:
            text = self.sort
        if not text:
            text = str(self.id)
        return text

    def __str__(self):
        return f'Phrase {self.id} "{self.name()}"'
    
    def correct_groups_qty(self, mode, group_id=None):
        group = get_object_or_404(CramGroup, pk=group_id)
        if (group.determinator == 'group') or (group.determinator == None):
            match mode:
                case GroupQuantityCorrectMode.ADD_PHRASE:
                    if group.act_items_qty == None:
                        group.act_items_qty = 0
                    group.act_items_qty += 1
                    group.save()
                    return True
                case GroupQuantityCorrectMode.DEL_PHRASE:
                    if (group.act_items_qty != None) and (group.act_items_qty > 0):
                        group.act_items_qty -= 1
                        group.save()
                        return True
        return False
    
class LangPhrase(models.Model):
    phrase = models.ForeignKey(Phrase, on_delete=models.SET_NULL, verbose_name='Phrase Id', related_name='phrase', null=True)
    lang = models.ForeignKey(Lang, on_delete=models.SET_NULL, verbose_name='Language code', related_name='phrase_language_code', null=True)
    text = models.TextField('Phrase', blank=True, null=True)

class Training(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'training_user')
    group = models.ForeignKey(CramGroup, on_delete=models.CASCADE, verbose_name='Group', blank=True, null=True)
    start = models.DateTimeField('Training start time', null=False, default=datetime.now)
    stop = models.DateTimeField('Training stop time', null=True)
    ratio = models.DecimalField('Training ratio', null=True, max_digits=15, decimal_places=3)
    total = models.IntegerField('Total phrases', null=False)
    passed = models.IntegerField('Passed phrases', null=False, default=0)

class TrainingPhrase(models.Model):
    training = models.ForeignKey(Training, on_delete=models.CASCADE, verbose_name='Training', related_name = 'tp_training')
    phrase = models.ForeignKey(Phrase, on_delete=models.SET_NULL, verbose_name='Phrase Id', related_name='tp_phrase', null=True)
    lang = models.ForeignKey(Lang, on_delete=models.SET_NULL, verbose_name='Language code', related_name='training_phrase_language', null=True)
    pass_time = models.DateTimeField('Pass time', null=False, default=datetime.now)
    ratio = models.DecimalField('Training ratio', null=True, max_digits=15, decimal_places=3)


    