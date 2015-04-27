import datetime

from django.utils import timezone
from django.test import TestCase

from fuel.models import Car, Fuel

class FuelMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        self.assertEqual(1+1, 3)