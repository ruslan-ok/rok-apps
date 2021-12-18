from django.apps import AppConfig
from trip.config import app_config


class TripConfig(AppConfig):
    name = app_config['name']
