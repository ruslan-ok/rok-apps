from django.apps import AppConfig
from expen.config import app_config

class ExpenConfig(AppConfig):
    name = app_config['name']
