from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.
class UserExt(models.Model):
    # required to associate UserExt model with User model (Important)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('user'))

    # additional fields
    phone = models.CharField(_('phone'), max_length=100, blank=True)
    activation_key = models.CharField(_('activation key'), max_length=255, default=1)
    email_validated = models.BooleanField(_('email validated'), default=False)
    avatar = models.ImageField(_('avatar').capitalize(), blank=True, upload_to='avatars/')
    avatar_mini = models.ImageField(_('avatar thumbnail').capitalize(), blank=True, upload_to='avatars/thumbnails/')

    class Meta:
        verbose_name = _('user extension')
        verbose_name_plural = _('users extensions')

    def __str__(self):
        return self.user.username
