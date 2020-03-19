from django.db import models
#from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class UserExt(models.Model):
    # required to associate UserExt model with User model (Important)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
 
    # additional fields
    phone = models.CharField(max_length=100, blank=True)
    activation_key = models.CharField(max_length=255, default=1)
    email_validated = models.BooleanField(default=False)
 
    def __str__(self):
        return self.user.username
 