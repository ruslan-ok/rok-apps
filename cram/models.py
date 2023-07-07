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
        # self.user = self.request.user
        super().save(*args, **kwargs)

# class CramGroupFlt(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user', related_name='cram_group')
#     app = models.CharField('app name', max_length=50, blank=False, default=APP_CRAM, null=True)
#     role = models.CharField('role name', max_length=50, blank=False, default=ROLE_CRAM, null=True)
#     node = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='node', blank=True, null=True)
#     name = models.CharField('group name', max_length=200, blank=False)
#     sort = models.CharField('sort code', max_length=50, blank=True)
#     info = models.TextField('information', blank=True, null=True)

#     class Meta:
#         db_table = 'task_group'
#         managed = False

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
    sort = models.fields.CharField('Sort code', max_length=10, null=True)
    categories = models.TextField('Categories', blank=True, null=True)

    def __str__(self):
        text = ''
        if Lang.objects.filter(user=self.user.id, code="ru").exists():
            ru = Lang.objects.filter(user=self.user.id, code="ru").get()
            if LangPhrase.objects.filter(phrase=self.id, lang=ru.id).exists():
                lp = LangPhrase.objects.filter(phrase=self.id, lang=ru.id).get()
                text = lp.text
        return f'Phrase {self.id} "{self.sort}" {text}'

class LangPhrase(models.Model):
    phrase = models.ForeignKey(Phrase, on_delete=models.SET_NULL, verbose_name='Phrase Id', related_name='phrase', null=True)
    lang = models.ForeignKey(Lang, on_delete=models.SET_NULL, verbose_name='Language code', related_name='phrase_language_code', null=True)
    text = models.TextField('Phrase', blank=True, null=True)
