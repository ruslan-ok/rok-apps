from django.apps import AppConfig
from health.config import app_config

class HealthConfig(AppConfig):
    name = app_config['name']
