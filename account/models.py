from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

EN = 0
RU = 1
LANG_CHOICE   = [(EN, 'English'), (RU, 'Русский')]

# Create your models here.
class UserExt(models.Model):
    # required to associate UserExt model with User model (Important)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('user'))

    # additional fields
    phone = models.CharField(_('phone'), max_length=100, blank=True)
    activation_key = models.CharField(_('activation key'), max_length=255, default=1)
    email_validated = models.BooleanField(_('email validated'), default=False)
    avatar = models.ImageField(_('avatar').capitalize(), blank=True, upload_to='avatars/', null=True)
    avatar_mini = models.ImageField(_('avatar thumbnail').capitalize(), blank=True, upload_to='avatars/thumbnails/', null=True)
    fuel_notice = models.DateTimeField(_('Service Interval Notification Time'), null=True)
    lang = models.IntegerField(_('Mailing list language'), choices=LANG_CHOICE, default=EN, null=True)

    class Meta:
        verbose_name = _('user extension')
        verbose_name_plural = _('users extensions')

    def __str__(self):
        return self.user.username
