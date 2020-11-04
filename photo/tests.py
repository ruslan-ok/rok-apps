from django.test import TestCase
from django.contrib.auth.models import User
from .views import get_thumbnail

class PhotoTests(TestCase):

    def test_thumb(self):
        self.user = User.objects.create(username = 'tests.py')
        self.name = 'Inbox/20191117_142026.jpg'
        get_thumbnail(self.user, self.name)
        self.user.delete()



