from django.apps import AppConfig
from fuel.config import app_config


class FuelConfig(AppConfig):
    name = app_config['name']
