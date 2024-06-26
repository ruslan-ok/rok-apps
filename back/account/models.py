from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.
class UserExt(models.Model):
    # required to associate UserExt model with User model (Important)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('User'))

    # additional fields
    phone = models.CharField(_('Phone'), max_length=100, blank=True)
    activation_key = models.CharField(_('Activation key'), max_length=255, default=1)
    email_validated = models.BooleanField(_('Email validated'), default=False)
    avatar = models.ImageField(_('Avatar'), blank=True, upload_to='avatars/', null=True)
    avatar_mini = models.ImageField(_('Avatar thumbnail'), blank=True, upload_to='avatars/thumbnails/', null=True)

    class Meta:
        verbose_name = _('User extension')
        verbose_name_plural = _('Users extensions')

    def __str__(self):
        return self.user.username
