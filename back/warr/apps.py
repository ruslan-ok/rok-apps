from django.apps import AppConfig
from warr.config import app_config

class WarrConfig(AppConfig):
    name = app_config['name']
