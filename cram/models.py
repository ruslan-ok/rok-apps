from django.db import models
from django.db.models import Manager
from django.contrib.auth.models import User
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

class Phrase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'cram_user')
    grp = models.ForeignKey(CramGroup, on_delete=models.CASCADE, verbose_name='Group', blank=True, null=True)
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
    
class LangPhrase(models.Model):
    phrase = models.ForeignKey(Phrase, on_delete=models.SET_NULL, verbose_name='Phrase Id', related_name='phrase', null=True)
    lang = models.ForeignKey(Lang, on_delete=models.SET_NULL, verbose_name='Language code', related_name='phrase_language_code', null=True)
    text = models.TextField('Phrase', blank=True, null=True)
